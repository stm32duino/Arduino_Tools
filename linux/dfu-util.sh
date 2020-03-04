#!/bin/bash
#
# Use the correct dfu-util program based on the architecture
#

# Get the directory where the script is running.
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Choose dfu program by arch
if [ "$(uname -m)" == "x86_64" ]; then
  DFU_UTIL=${DIR}/dfu-util_x86_64/dfu-util
else
  DFU_UTIL=${DIR}/dfu-util/dfu-util
fi

# Not found!
if [ ! -x "${DFU_UTIL}" ]; then
  echo "$0: error: cannot find ${DFU_UTIL}" >&2
  exit 2
fi

# Pass all parameters through
"${DFU_UTIL}" "$@"
