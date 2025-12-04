#!/bin/sh -
#
# Use the correct hid-flash program based on the host
#

# Get the directory where the script is running.
DIR=$(cd "$(dirname "$0")" && pwd)
UNAME_OS="$(uname -s)"
case "${UNAME_OS}" in
  Linux*)
    # Choose program by arch
    UNAME_ARCH="$(uname -m)"
    case "${UNAME_ARCH}" in
      x86_64)
        HID_FLASH=${DIR}/linux/x86_64/hid-flash
        ;;
      aarch64|arm64)
        HID_FLASH=${DIR}/linux/aarch64/hid-flash
        ;;
      *)
        echo "Unsupported Linux architecture: ${UNAME_ARCH}."
        exit 1
        ;;
    esac
    ;;
  Darwin*)
    HID_FLASH=${DIR}/macosx/hid-flash
    ;;
  Windows*)
    HID_FLASH=${DIR}/win/hid-flash.exe
    ;;
  *)
    echo "Unknown host OS: ${UNAME_OS}."
    exit 1
    ;;
esac

# Not found!
if [ ! -x "${HID_FLASH}" ]; then
  echo "$0: error: cannot find ${HID_FLASH}" >&2
  exit 2
fi

# Pass all parameters through
"${HID_FLASH}" "$@"
