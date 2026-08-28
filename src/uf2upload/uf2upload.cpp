/*
 * SPDX-License-Identifier: GPL-2.0-or-later
 *
 * Cross-platform UF2 uploader for Arduino boards using a USB CDC touch and
 * a UF2 mass-storage bootloader.
 */

#include <algorithm>
#include <array>
#include <chrono>
#include <climits>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <termios.h>
#include <unistd.h>
#endif

namespace {

constexpr uint32_t UF2_MAGIC_START0 = 0x0A324655UL;
constexpr uint32_t UF2_MAGIC_START1 = 0x9E5D5157UL;
constexpr uint32_t UF2_MAGIC_END = 0x0AB16F30UL;
constexpr uint32_t UF2_FLAG_FAMILY_ID_PRESENT = 0x00002000UL;
constexpr size_t UF2_BLOCK_SIZE = 512U;
constexpr size_t UF2_PAYLOAD_SIZE = 256U;

struct Options {
  std::string input;
  std::string port;
  std::string volume;
  uint32_t address = 0U;
  uint32_t family = 0U;
  size_t max_size = 0U;
  unsigned int timeout_ms = 10000U;
  bool skip_touch = false;
};

void usage(const char *program)
{
  std::cout << "Usage: " << program << " --input <firmware.bin> [--port <serial-port>]"
            << " --volume <label> --address <base-address> --family <uf2-family-id>"
            << " [--max-size <bytes>] [--timeout <milliseconds>] [--skip-touch]\n"
            << "\n"
            << "Performs: detect an existing UF2 volume -> otherwise 1200-bps CDC touch"
            << " -> wait for volume -> UF2 conversion -> copy.\n"
            << "--skip-touch disables the CDC touch when a bootloader volume is not yet present.\n";
}

bool parse_unsigned(const std::string &value, uint64_t *result)
{
  try {
    size_t consumed = 0U;
    const uint64_t parsed = std::stoull(value, &consumed, 0);
    if (consumed != value.length()) {
      return false;
    }
    *result = parsed;
    return true;
  } catch (const std::exception &) {
    return false;
  }
}

bool parse_options(int argc, char *argv[], Options *options)
{
  for (int index = 1; index < argc; ++index) {
    const std::string argument = argv[index];
    if (argument == "--help" || argument == "-h") {
      usage(argv[0]);
      std::exit(0);
    }
    if (argument == "--skip-touch") {
      options->skip_touch = true;
      continue;
    }
    if (index + 1 >= argc) {
      std::cerr << "Missing value for " << argument << "\n";
      return false;
    }

    const std::string value = argv[++index];
    uint64_t number = 0U;
    if (argument == "--input") {
      options->input = value;
    } else if (argument == "--port") {
      options->port = value;
    } else if (argument == "--volume") {
      options->volume = value;
    } else if (argument == "--address") {
      if (!parse_unsigned(value, &number) || number > UINT32_MAX) {
        std::cerr << "Invalid --address: " << value << "\n";
        return false;
      }
      options->address = static_cast<uint32_t>(number);
    } else if (argument == "--family") {
      if (!parse_unsigned(value, &number) || number > UINT32_MAX) {
        std::cerr << "Invalid --family: " << value << "\n";
        return false;
      }
      options->family = static_cast<uint32_t>(number);
    } else if (argument == "--max-size") {
      if (!parse_unsigned(value, &number) || number == 0U || number > SIZE_MAX) {
        std::cerr << "Invalid --max-size: " << value << "\n";
        return false;
      }
      options->max_size = static_cast<size_t>(number);
    } else if (argument == "--timeout") {
      if (!parse_unsigned(value, &number) || number == 0U || number > UINT_MAX) {
        std::cerr << "Invalid --timeout: " << value << "\n";
        return false;
      }
      options->timeout_ms = static_cast<unsigned int>(number);
    } else {
      std::cerr << "Unknown option: " << argument << "\n";
      return false;
    }
  }

  if (options->input.empty() || options->volume.empty() || options->address == 0U || options->family == 0U) {
    std::cerr << "Missing required option.\n";
    return false;
  }
  return true;
}

void write_u32(std::ofstream *stream, uint32_t value)
{
  const std::array<uint8_t, 4> bytes = {
    static_cast<uint8_t>(value),
    static_cast<uint8_t>(value >> 8U),
    static_cast<uint8_t>(value >> 16U),
    static_cast<uint8_t>(value >> 24U),
  };
  stream->write(reinterpret_cast<const char *>(bytes.data()), bytes.size());
}

bool read_file(const std::string &path, size_t max_size, std::vector<uint8_t> *image)
{
  std::ifstream stream(path, std::ios::binary | std::ios::ate);
  if (!stream) {
    std::cerr << "Unable to open input image: " << path << "\n";
    return false;
  }
  const std::streamsize length = stream.tellg();
  if (length <= 0) {
    std::cerr << "Input image is empty: " << path << "\n";
    return false;
  }
  if (max_size != 0U && static_cast<uint64_t>(length) > max_size) {
    std::cerr << "Input image exceeds the board maximum of " << max_size << " bytes.\n";
    return false;
  }
  image->resize(static_cast<size_t>(length));
  stream.seekg(0, std::ios::beg);
  stream.read(reinterpret_cast<char *>(image->data()), length);
  if (!stream) {
    std::cerr << "Unable to read input image: " << path << "\n";
    return false;
  }
  return true;
}

std::string temporary_uf2_path()
{
#ifdef _WIN32
  std::array<char, MAX_PATH> temp_path{};
  const DWORD length = GetTempPathA(static_cast<DWORD>(temp_path.size()), temp_path.data());
  if (length == 0U || length >= temp_path.size()) {
    return "xiao-stm32-uf2-upload.tmp";
  }
  return std::string(temp_path.data()) + "xiao-stm32-uf2-" + std::to_string(GetCurrentProcessId()) + ".uf2";
#else
  const char *temp_dir = std::getenv("TMPDIR");
  if (temp_dir == nullptr || *temp_dir == '\0') {
    temp_dir = "/tmp";
  }
  return std::string(temp_dir) + "/xiao-stm32-uf2-" + std::to_string(getpid()) + ".uf2";
#endif
}

bool make_uf2(const std::vector<uint8_t> &image, const Options &options, const std::string &path)
{
  const size_t blocks = (image.size() + UF2_PAYLOAD_SIZE - 1U) / UF2_PAYLOAD_SIZE;
  if (blocks > UINT32_MAX || static_cast<uint64_t>(options.address) + image.size() > UINT32_MAX) {
    std::cerr << "UF2 address range is invalid.\n";
    return false;
  }

  std::ofstream stream(path, std::ios::binary | std::ios::trunc);
  if (!stream) {
    std::cerr << "Unable to create temporary UF2 image: " << path << "\n";
    return false;
  }

  for (size_t block = 0U; block < blocks; ++block) {
    const size_t offset = block * UF2_PAYLOAD_SIZE;
    const size_t size = std::min(UF2_PAYLOAD_SIZE, image.size() - offset);
    std::array<uint8_t, UF2_PAYLOAD_SIZE> payload{};
    std::memcpy(payload.data(), image.data() + offset, size);

    write_u32(&stream, UF2_MAGIC_START0);
    write_u32(&stream, UF2_MAGIC_START1);
    write_u32(&stream, UF2_FLAG_FAMILY_ID_PRESENT);
    write_u32(&stream, options.address + static_cast<uint32_t>(offset));
    write_u32(&stream, UF2_PAYLOAD_SIZE);
    write_u32(&stream, static_cast<uint32_t>(block));
    write_u32(&stream, static_cast<uint32_t>(blocks));
    write_u32(&stream, options.family);
    stream.write(reinterpret_cast<const char *>(payload.data()), payload.size());
    std::array<uint8_t, UF2_BLOCK_SIZE - 32U - UF2_PAYLOAD_SIZE - 4U> padding{};
    stream.write(reinterpret_cast<const char *>(padding.data()), padding.size());
    write_u32(&stream, UF2_MAGIC_END);
  }

  if (!stream) {
    std::cerr << "Unable to write temporary UF2 image.\n";
    return false;
  }
  std::cout << "Created UF2 image with " << blocks << " block(s).\n";
  return true;
}

std::string basename(const std::string &path)
{
  const size_t separator = path.find_last_of("/\\");
  return separator == std::string::npos ? path : path.substr(separator + 1U);
}

#ifdef _WIN32
std::wstring wide_string(const std::string &text)
{
  if (text.empty()) {
    return {};
  }
  int length = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, text.data(), static_cast<int>(text.size()), nullptr, 0);
  UINT codepage = CP_UTF8;
  if (length == 0) {
    codepage = CP_ACP;
    length = MultiByteToWideChar(codepage, 0, text.data(), static_cast<int>(text.size()), nullptr, 0);
  }
  if (length == 0) {
    return {};
  }
  std::wstring result(static_cast<size_t>(length), L'\0');
  MultiByteToWideChar(codepage, 0, text.data(), static_cast<int>(text.size()), result.data(), length);
  return result;
}

bool touch_serial(const std::string &port)
{
  std::wstring device = wide_string(port);
  if (device.empty()) {
    std::cerr << "Invalid serial port name.\n";
    return false;
  }
  if (device.rfind(L"\\\\.\\", 0U) != 0U) {
    device = L"\\\\.\\" + device;
  }
  const HANDLE handle = CreateFileW(device.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
  if (handle == INVALID_HANDLE_VALUE) {
    std::cerr << "Unable to open serial port " << port << " (Windows error " << GetLastError() << ").\n";
    return false;
  }

  DCB dcb{};
  dcb.DCBlength = sizeof(dcb);
  if (GetCommState(handle, &dcb) == 0) {
    const DWORD error = GetLastError();
    CloseHandle(handle);
    std::cerr << "Unable to read serial settings from " << port << " (Windows error " << error << ").\n";
    return false;
  }

  dcb.BaudRate = CBR_1200;
  dcb.fBinary = TRUE;
  const bool applied = SetCommState(handle, &dcb) != 0;
  const DWORD error = applied ? ERROR_SUCCESS : GetLastError();
  CloseHandle(handle);

  if (applied) {
    std::cout << "1200-bps line coding applied; waiting for the bootloader.\n";
    return true;
  }

  /* A CDC device may reset while Windows is completing SET_LINE_CODING.  The
   * bootloader-volume wait below decides whether that request still reached
   * the application, but the error must stay visible for diagnosis. */
  std::cout << "1200-bps line coding returned Windows error " << error
            << "; the device may have reset during the request. Waiting for the bootloader.\n";
  return true;
}

std::string find_volume(const std::string &label)
{
  const std::wstring expected = wide_string(label);
  for (wchar_t letter = L'A'; letter <= L'Z'; ++letter) {
    const std::wstring root = std::wstring(1U, letter) + L":\\";
    if (GetDriveTypeW(root.c_str()) == DRIVE_NO_ROOT_DIR) {
      continue;
    }
    std::array<wchar_t, MAX_PATH + 1U> actual{};
    if (GetVolumeInformationW(root.c_str(), actual.data(), static_cast<DWORD>(actual.size()), nullptr, nullptr, nullptr,
                              nullptr, 0U) != 0 && expected == actual.data()) {
      return std::string(1U, static_cast<char>(letter)) + ":\\";
    }
  }
  return {};
}

bool copy_file(const std::string &source, const std::string &directory)
{
  const std::wstring destination = wide_string(directory + basename(source));
  if (CopyFileW(wide_string(source).c_str(), destination.c_str(), FALSE) == 0) {
    std::cerr << "Unable to copy UF2 to " << directory << " (Windows error " << GetLastError() << ").\n";
    return false;
  }
  return true;
}
#else
bool touch_serial(const std::string &port)
{
  const int fd = open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (fd < 0) {
    std::perror(("Unable to open serial port " + port).c_str());
    return false;
  }
  termios settings{};
  const bool success = tcgetattr(fd, &settings) == 0 && cfsetispeed(&settings, B1200) == 0 &&
                       cfsetospeed(&settings, B1200) == 0 && tcsetattr(fd, TCSANOW, &settings) == 0;
  if (!success) {
    std::perror("Unable to set serial port to 1200 bps");
  }
  close(fd);
  return success;
}

bool is_directory(const std::string &path)
{
  struct stat status {};
  return stat(path.c_str(), &status) == 0 && S_ISDIR(status.st_mode);
}

std::string find_volume_in(const std::string &root, const std::string &label, unsigned int depth)
{
  DIR *directory = opendir(root.c_str());
  if (directory == nullptr) {
    return {};
  }
  std::string found;
  while (dirent *entry = readdir(directory)) {
    const std::string name = entry->d_name;
    if (name == "." || name == "..") {
      continue;
    }
    const std::string path = root + "/" + name;
    if (!is_directory(path)) {
      continue;
    }
    if (name == label) {
      found = path + "/";
      break;
    }
    if (depth != 0U) {
      found = find_volume_in(path, label, depth - 1U);
      if (!found.empty()) {
        break;
      }
    }
  }
  closedir(directory);
  return found;
}

std::string find_volume(const std::string &label)
{
  const std::array<const char *, 4> roots = {"/Volumes", "/media", "/run/media", "/mnt"};
  for (const char *root : roots) {
    const std::string found = find_volume_in(root, label, 2U);
    if (!found.empty()) {
      return found;
    }
  }
  return {};
}

bool copy_file(const std::string &source, const std::string &directory)
{
  std::ifstream input(source, std::ios::binary);
  std::ofstream output(directory + basename(source), std::ios::binary | std::ios::trunc);
  output << input.rdbuf();
  if (!input && !input.eof()) {
    std::cerr << "Unable to read generated UF2 image.\n";
    return false;
  }
  if (!output) {
    std::cerr << "Unable to copy UF2 to " << directory << ".\n";
    return false;
  }
  return true;
}
#endif

std::string wait_for_volume(const Options &options)
{
  const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(options.timeout_ms);
  do {
    const std::string volume = find_volume(options.volume);
    if (!volume.empty()) {
      return volume;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  } while (std::chrono::steady_clock::now() < deadline);
  return {};
}

} // namespace

int main(int argc, char *argv[])
{
  Options options;
  if (!parse_options(argc, argv, &options)) {
    usage(argv[0]);
    return 2;
  }

  std::vector<uint8_t> image;
  if (!read_file(options.input, options.max_size, &image)) {
    return 3;
  }

  const std::string uf2_path = temporary_uf2_path();
  if (!make_uf2(image, options, uf2_path)) {
    return 4;
  }

  std::string volume = find_volume(options.volume);
  if (!volume.empty()) {
    std::cout << "Bootloader volume " << options.volume << " already present at " << volume
              << "; skipping 1200-bps touch.\n";
  } else if (!options.skip_touch) {
    if (options.port.empty()) {
      std::cerr << "No bootloader volume is present and no serial port was supplied for the 1200-bps touch.\n";
      std::remove(uf2_path.c_str());
      return 5;
    }
    std::cout << "Sending 1200-bps touch to " << options.port << ".\n";
    if (!touch_serial(options.port)) {
      std::remove(uf2_path.c_str());
      return 5;
    }
  }

  if (volume.empty()) {
    std::cout << "Waiting for volume " << options.volume << ".\n";
    volume = wait_for_volume(options);
  }
  if (volume.empty()) {
    std::cerr << "Timed out waiting for volume " << options.volume << ".\n";
    std::remove(uf2_path.c_str());
    return 6;
  }

  std::cout << "Bootloader volume " << options.volume << " found at " << volume << ".\n";
  std::cout << "Copying UF2 to " << volume << ".\n";
  const bool copied = copy_file(uf2_path, volume);
  std::remove(uf2_path.c_str());
  if (!copied) {
    return 7;
  }
  std::cout << "Upload successful: UF2 copied to " << options.volume << ".\n";
  std::cout << "Done uploading.\n";
  return 0;
}
