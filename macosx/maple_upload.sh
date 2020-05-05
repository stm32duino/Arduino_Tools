#!/bin/bash

set -e

if [ $# -lt 4 ]; then
  echo "Usage: $0 $# <dummy_port> <altID> <usbID> <binfile>" >&2
  exit 1
fi
altID="$2"
usbID="$3"
binfile="$4"
dummy_port_fullpath="/dev/$1"
if [ $# -eq 5 ]; then
  dfuse_addr="--dfuse-address $5"
else
  dfuse_addr=""
fi

# Get the directory where the script is running.
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

#  ----------------- IMPORTANT -----------------
# The 2nd parameter to upload-reset is the delay after resetting before it exits
# This value is in milliseonds
# You may need to tune this to your system
# 750ms to 1500ms seems to work on my Mac
# This is less critical now that we automatically retry dfu-util

if ! "${DIR}/upload-reset" "${dummy_port_fullpath}" 750; then
  echo "****************************************" >&2
  echo "* Could not automatically reset device *" >&2
  echo "* Please manually reset device!        *" >&2
  echo "****************************************" >&2
  sleep 2 # Wait for user to see message.
fi

COUNTER=5
while
  "${DIR}/dfu-util.sh" -d "${usbID}" -a "${altID}" -D "${binfile}" ${dfuse_addr} -R
  ((ret = $?))
do
  if [ $ret -eq 74 ] && [ $((--COUNTER)) -gt 0 ]; then
    # I/O error, probably because no DFU device was found
    echo "Trying ${COUNTER} more time(s)" >&2
    sleep 1
  else
    exit $ret
  fi
done

echo -n "Waiting for ${dummy_port_fullpath} serial..." >&2

COUNTER=40
while [ ! -r "${dummy_port_fullpath}" ] && ((COUNTER--)); do
  echo -n "." >&2
  sleep 0.1
done

if [ $COUNTER -eq -1 ]; then
  echo " Timed out." >&2
  exit 1
else
  echo " Done." >&2
fi
