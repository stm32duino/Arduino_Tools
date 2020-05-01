#!/bin/bash

# Get the directory where the script is running.
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

DFU_UTIL=${DIR}/dfu-util/dfu-util
if [ ! -x "${DFU_UTIL}" ]; then
  DFU_UTIL=/opt/local/bin/dfu-util
fi

# Not found!
if [ ! -x "${DFU_UTIL}" ]; then
  echo "$0: error: cannot find ${DFU_UTIL}" >&2
  exit 2
fi

# Pass all parameters through
"${DFU_UTIL}" "$@"
