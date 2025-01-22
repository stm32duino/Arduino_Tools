#!/bin/sh

set -eu

[ -z "${ARCH+x}" ] && ARCH=universal

case "${ARCH}" in
  arm64)
    # Build for arm64, either as a same-architecture or cross-architecture
    # build.
    CONFIGURE_HOST_ARG="--host=aarch64-apple-darwin"
    CC_ARCH_ARG="-arch ${ARCH}"

    # Don't collide with macosx, which has traditionally been used for x86_64
    # code.
    ARCH_DIR=mac-arm64
    ;;
  universal)
    # Build for x86_64 and arm64 simultaneously, putting the results into
    # "universal" or "fat" binaries.
    CONFIGURE_HOST_ARG=
    CC_ARCH_ARG="-arch x86_64 -arch arm64"

    # It's fine to put universal code into macosx, traditionally used for x86_64
    # code, because it will contain x86_64 code and will run without trouble on
    # x86_64 systems. Using the same directory for universal files means that
    # these tools will remain at a stable path across a transition between
    # x86_64 and arm64.
    ARCH_DIR=macosx
    ;;
  x86_64)
    # Build for x86_64, either as a same-architecture or cross-architecture
    # build.
    CONFIGURE_HOST_ARG="--host=${ARCH}-apple-darwin"
    CC_ARCH_ARG="-arch ${ARCH}"

    ARCH_DIR=macosx
    ;;
  *)
    # Build for some other ${ARCH}, either as a same-architecture or
    # cross-architecture build.
    CONFIGURE_HOST_ARG="--host=${ARCH}-apple-darwin"
    CC_ARCH_ARG="-arch ${ARCH}"

    ARCH_DIR="mac-${ARCH}"
    ;;
esac

if [ -z "${MIN_OS_VERSION+x}" ]; then
  case "${ARCH}" in
    arm64)
      # macOS 11 was the first to support arm64.
      MIN_OS_VERSION=11.0
      ;;
    universal | x86_64)
      # Although this could be set lower, the xPack tools declare support for
      # macOS 10.13, so it's unlikely that anyone would be using anything older.
      #
      # In a universal build, the toolchain will use this value for the x86_64
      # build, but will automatically increase the minimum to 11.0 for the arm64
      # build, because that was the first OS version to support arm64.
      MIN_OS_VERSION=10.13
      ;;
  esac
fi
if [ -n "${MIN_OS_VERSION+x}" ]; then
  CC_MIN_OS_VERSION_ARG="-mmacosx-version-min=${MIN_OS_VERSION}"
fi

MAKE_J_ARG="-j$(sysctl -n hw.ncpu)"
BASE_CFLAGS="-Os -flto"
BASE_LDFLAGS="-dead_strip"

LIBUSB_VERSION=1.0.27
DFU_UTIL_VERSION=0.11
STM32_HID_BOOTLOADER_VERSION=2.2.2

set -x

cd "$(dirname "${0}")/.."

(
  cd ..

  # dfu-util depends on libusb, which isn't part of the operating system.
  # Provide a build of libusb to satisfy that dependency.
  [ ! -d libusb ] && git clone https://github.com/libusb/libusb.git
  cd libusb
  git checkout "v${LIBUSB_VERSION}"
  # git clean -fdx
  # git checkout -- .
  sh bootstrap.sh
  CC="clang ${CC_ARCH_ARG} ${CC_MIN_OS_VERSION_ARG}" \
    CFLAGS="${BASE_CFLAGS}" \
    LDFLAGS="${BASE_LDFLAGS} -Wl,-source_version,${LIBUSB_VERSION}" \
    sh configure ${CONFIGURE_HOST_ARG}
  make clean
  make ${MAKE_J_ARG}

  # Rewrite the LC_ID_DYLIB in libusb-1.0.0.dylib so that other modules that
  # link against it will expect to find it in the same directory that they are
  # located in (@loader_path). Later, libusb-1.0.0.dylib will be copied to the
  # same directory as dfu-util and the other executables that rely on it.
  install_name_tool \
    -id @loader_path/libusb-1.0.0.dylib \
    libusb/.libs/libusb-1.0.0.dylib

  cd ..

  [ ! -d dfu-util ] && git clone git://git.code.sf.net/p/dfu-util/dfu-util
  cd dfu-util
  git checkout "v${DFU_UTIL_VERSION}"
  # git clean -fdx
  # git checkout -- .
  sh autogen.sh
  CC="clang ${CC_ARCH_ARG} ${CC_MIN_OS_VERSION_ARG}" \
    CFLAGS="${BASE_CFLAGS} -fvisibility=hidden" \
    LDFLAGS="${BASE_LDFLAGS} -Wl,-source_version,${DFU_UTIL_VERSION}" \
    USB_CFLAGS="-I$(pwd)/../libusb/libusb" \
    USB_LIBS="-L$(pwd)/../libusb/libusb/.libs -lusb-1.0.0" \
    sh configure ${CONFIGURE_HOST_ARG}
  make clean
  make ${MAKE_J_ARG}
  cd ..

  [ ! -d STM32_HID_Bootloader ] &&
    git clone https://github.com/Serasidis/STM32_HID_Bootloader.git
  cd STM32_HID_Bootloader
  git checkout "${STM32_HID_BOOTLOADER_VERSION}"
  # git clean -fdx
  # git checkout -- .
  git checkout -- cli/main.c

  # Isolate and apply the patch from
  # https://github.com/Serasidis/STM32_HID_Bootloader/issues/68#issuecomment-2009105851
  curl --silent \
    https://api.github.com/repos/Serasidis/STM32_HID_Bootloader/issues/comments/2009105851 |
    jq --raw-output .body |
    sed -e 's/\r//g' -e '1,/^```/d' -e '/^```$/,$d' |
    patch cli/main.c

  make -C cli clean
  make -C cli ${MAKE_J_ARG} \
    CC="clang ${CC_ARCH_ARG} ${CC_MIN_OS_VERSION_ARG}" \
    CFLAGS="${BASE_CFLAGS} -fvisibility=hidden -Wall -Werror -c" \
    LDFLAGS="${BASE_LDFLAGS} -Wl,-source_version,${STM32_HID_BOOTLOADER_VERSION}"
  cd ..
)

mkdir -p "${ARCH_DIR}"

cp ../libusb/libusb/.libs/libusb-1.0.0.dylib \
  ../dfu-util/src/dfu-prefix \
  ../dfu-util/src/dfu-suffix \
  ../dfu-util/src/dfu-util \
  ../STM32_HID_Bootloader/cli/hid-flash \
  "${ARCH_DIR}/"
chmod -x "${ARCH_DIR}/libusb-1.0.0.dylib"

# It would be nice to include -Wl,-source_version here, but that's tricky to do
# for code that's in this repository, and probably won't be tagged with a
# version until after this tool is built.
clang \
  ${CC_ARCH_ARG} \
  ${CC_MIN_OS_VERSION_ARG} \
  ${BASE_CFLAGS} \
  -fvisibility=hidden \
  ${BASE_LDFLAGS} \
  -Wall \
  -Werror \
  -o "${ARCH_DIR}/upload_reset" \
  src/upload_reset/unix/upload_reset.c
