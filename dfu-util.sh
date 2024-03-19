#!/bin/sh -
#
# Use the correct dfu-util program based on the host
#

# Get the directory where the script is running.
DIR=$(cd "$(dirname "$0")" && pwd)
UNAME_OS="$(uname -s)"
case "${UNAME_OS}" in
  Linux*)
    # Choose dfu program by arch
    DFU_UTIL=${DIR}/linux/dfu-util/dfu-util
    ;;
  Darwin*)
    DFU_UTIL=${DIR}/macosx/dfu-util/dfu-util
    if [ ! -x "${DFU_UTIL}" ]; then
      DFU_UTIL=/opt/local/bin/dfu-util
    fi
    ;;
  Windows*)
    DFU_UTIL=${DIR}/win/dfu-util.exe
    ;;
  *)
    echo "Unknown host OS: ${UNAME_OS}."
    exit 1
    ;;
esac

# Not found!
if [ ! -x "${DFU_UTIL}" ]; then
  echo "$0: error: cannot find ${DFU_UTIL}" >&2
  exit 2
fi

# Pass all parameters through
"${DFU_UTIL}" "$@"
