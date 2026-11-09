# Arduino_Tools
[![GitHub release](https://img.shields.io/github/release/stm32duino/Arduino_Tools.svg)](https://github.com/stm32duino/Arduino_Tools/releases/latest)
[![GitHub commits](https://img.shields.io/github/commits-since/stm32duino/Arduino_Tools/2.5.0.svg)](https://github.com/stm32duino/Arduino_Tools/compare/2.4.0...main)

Contains upload tools for STM32 based boards and some other useful scripts.

This repository is packaged and distributed as the `STM32Tools` tool dependency of the
[Arduino_Core_STM32](https://github.com/stm32duino/Arduino_Core_STM32) platform
(`{runtime.tools.STM32Tools.path}` in its `platform.txt`). The tools are installed automatically
by the Arduino Boards Manager along with the core and are not meant to be used standalone.

## Content

### Upload scripts

| Script | Description |
|--------|-------------|
| `stm32CubeProg.sh` | Wrapper for [STM32CubeProgrammer CLI](https://www.st.com/en/development-tools/stm32cubeprog.html) (must be installed or available in the `PATH`). Supports the `swd`, `dfu`, `serial` and `jlink` interfaces. Run it without argument to get the full list of options. |
| `dfu-util.sh` | Selects and runs the `dfu-util` binary matching the host OS and architecture. |
| `hid-flash.sh` | Selects and runs the `hid-flash` binary matching the host OS and architecture (HID bootloader v2.2 for STM32F1 and STM32F4 series). |
| `maple_upload.sh` | Uploads a binary to boards using the Maple bootloader over DFU: `maple_upload.sh <dummy_port> <altID> <usbVID> <usbPID> <binfile>`. |
| `linux/massStorageCopy.sh`<br>`macosx/massStorageCopy.sh`<br>`win/massStorageCopy.bat` | Copy a binary to a board exposed as a mass storage device (e.g. ST-LINK virtual drive of the Nucleo and Discovery boards). |

### STM32MP1 script

`run_arduino_gen.sh` is used for the STM32MP1 boards (Cortex-M4 firmware started from the Linux side
using remoteproc):

* `run_arduino_gen.sh generate <input ELF file> <output script file>`: generates a self-contained shell
  script embedding the ELF binary.
* The generated script supports `start`, `stop`, `restart`, `install` (auto-start at boot through a
  systemd service) and `uninstall`.

### Prebuilt binaries

| Directory | Content |
|-----------|---------|
| `linux/x86_64`, `linux/aarch64` | `dfu-util`, `dfu-prefix`, `dfu-suffix`, `hid-flash`, `upload_reset` |
| `macosx` | `dfu-util`, `dfu-prefix`, `dfu-suffix`, `hid-flash`, `upload_reset`, `libusb` |
| `win` | `dfu-util.exe`, `hid-flash.exe`, `upload_reset.exe`, `check_port.exe`, `busybox.exe` (to run the shell scripts), required DLLs. See [win/README.md](win/README.md) |

`upload_reset` sends the reset sequence (RTS/DTR and magic characters) to put a board running the
Maple bootloader into upload mode. `check_port` lists the serial ports or checks if a given one exists.

### Linux udev rules

* `linux/45-maple.rules`: udev rules for the Maple bootloader.
* `linux/99-stm32_hid_bl.rules`: udev rules for the STM32 HID bootloader.
* `linux/install.sh`: installs the Maple rules in `/etc/udev/rules.d` and adds the current user to the
  `dialout` group.

### Sources

The `src` directory contains the sources of the tools built in this repository:

* `src/upload_reset`: `upload_reset` (Unix and Windows).
* `src/check_port` and `src/libserialport`: `check_port` and the [libserialport](https://sigrok.org/wiki/Libserialport) library it uses.
* `src/build_mac.sh`: builds the macOS binaries.
* `src/linux-aarch64`: Docker based cross-compilation of the Linux aarch64 binaries,
  see [src/linux-aarch64/README.md](src/linux-aarch64/README.md).

## License

See [LICENSE.md](LICENSE.md).
