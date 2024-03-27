#!/bin/sh -

set -e

if [ $# -lt 5 ]; then
  echo "Usage: $0 <dummy_port> <altID> <usbVID> <usbPID> <binfile>" >&2
  exit 1
fi
altID="$2"
usbVID=${3#"0x"}
usbPID=${4#"0x"}
binfile="$5"
EXT=""

UNAME_OS="$(uname -s)"
case "${UNAME_OS}" in
  Linux*)
    dummy_port_fullpath="/dev/$1"
    OS_DIR="linux"
    ;;
  Darwin*)
    dummy_port_fullpath="/dev/$1"
    OS_DIR="macosx"
    ;;
  Windows*)
    dummy_port_fullpath="$1"
    OS_DIR="win"
    EXT=".exe"
    ;;
  *)
    echo "Unknown host OS: ${UNAME_OS}."
    exit 1
    ;;
esac

# Get the directory where the script is running.
DIR=$(cd "$(dirname "$0")" && pwd)

#  ----------------- IMPORTANT -----------------
# The 2nd parameter to upload_reset is the delay after resetting
# before it exits. This value is in milliseonds.
# You may need to tune this to your system
# 750ms to 1500ms seems to work on my Mac
# This is less critical now that we automatically retry dfu-util

if ! "${DIR}/${OS_DIR}/upload_reset${EXT}" "${dummy_port_fullpath}" 750; then
  echo "****************************************" >&2
  echo "* Could not automatically reset device *" >&2
  echo "* Please manually reset device!        *" >&2
  echo "****************************************" >&2
  sleep 2 # Wait for user to see message.
fi

COUNTER=5
while
  "${DIR}/dfu-util.sh" -d "${usbVID}:${usbPID}" -a "${altID}" -D "${binfile}" -R
  ret=$?
do
  if [ $ret -eq 0 ]; then
    break
  else
    COUNTER=$((COUNTER - 1))
    if [ $ret -eq 74 ] && [ $COUNTER -gt 0 ]; then
      # I/O error, probably because no DFU device was found
      echo "Trying ${COUNTER} more time(s)" >&2
      sleep 1
    else
      exit $ret
    fi
  fi
done

sleep 1

printf "Waiting for %s serial..." "${dummy_port_fullpath}"
COUNTER=40
if [ ${OS_DIR} = "win" ]; then
  while [ $COUNTER -gt 0 ]; do
    if ! "${DIR}/${OS_DIR}/check_port${EXT}" "${dummy_port_fullpath}"; then
      COUNTER=$((COUNTER - 1))
      printf "."
      sleep 0.1
    else
      break
    fi
  done

else
  while [ ! -r "${dummy_port_fullpath}" ] && [ $COUNTER -gt 0 ]; do
    COUNTER=$((COUNTER - 1))
    printf "."
    sleep 0.1
  done
fi

if [ $COUNTER -eq -0 ]; then
  echo " Timed out." >&2
  exit 1
else
  echo " Done."
fi
