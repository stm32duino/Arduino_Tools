#!/bin/bash
set -o nounset                              # Treat unset variables as an error
#set -x

# STM32 Cube programmer variables
STM32CP_CLI=STM32_Programmer.sh
ADDRESS=0x8000000
ERASE=
MODE=
PORT=
OPTS=

# Script variables
SERPORT=
STATUS=

###############################################################################
## Help function
usage()
{
  echo "############################################################"
  echo "##"
  echo "## `basename $0` <protocol> <file_path> [OPTIONS]"
  echo "##"
  echo "## protocol:"
  echo "##   0: SWD"
  echo "##   1: Serial"
  echo "##   2: DFU"
  echo "##   Note: prefix it by 1 to erase all sectors."
  echo "##         Ex: 10 erase all sectors using SWD interface."
  echo "## file_path: file path name to be downloaded: (bin, hex)"
  echo "## Options:"
  echo "##   For SWD: no mandatory options"
  echo "##   For DFU: no mandatory options"
  echo "##     Use '-serport=<com_port>' to request reset to bootloader mode"
  echo "##   For Serial: 'serport=<com_port>'"
  echo "##     com_port: serial identifier (mandatory). Ex: /dev/ttyS0"
  echo "##"
  echo "##   '-serport=<com_port>' is also used to wait the serial port availability"
  echo "## Note: all trailing arguments will be passed to the $STM32CP_CLI"
  echo "##   They have to be valid commands for STM32 MCU"
  echo "##   Ex: -g: Run the code at the specified address"
  echo "##       -rst: Reset system"
  echo "##       -s: start automatically (optional)"
  echo "############################################################"
  exit $1
}

check_tool() {
  command -v $STM32CP_CLI >/dev/null 2>&1
  if [ $? != 0 ]; then
    export PATH="$HOME/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin":$PATH
  fi
  command -v $STM32CP_CLI >/dev/null 2>&1
  if [ $? != 0 ]; then
    echo "$STM32CP_CLI not found."
    echo "Please install it or add '<STM32CubeProgrammer path>/bin' to your PATH environment:"
    echo "https://www.st.com/en/development-tools/stm32cubeprog.html"
    echo "Aborting!"
    exit 1
  fi
}

bootloaderMode() {
  if [ ! -z $SERPORT ]; then
    # Try to configure it at 1200 to restart
    # in Bootloader mode
    if [ -c $SERPORT ]; then
      count=0
      res=1
      while [ $res -ne 0 ] && ((count++ < 5)); do
        # echo "Try to set $SERPORT at 1200"
        stty -F $SERPORT 1200 > /dev/null 2>&1
        res=$?
        sleep 0.1
      done
      if [ $res -eq 0 ]; then
        sleep 0.5
      fi
    fi
  fi
}

upload() {
  count=0
  STATUS=1
  while [ $STATUS -ne 0 ] && ((count++ < 5)); do
    # echo "Try upload $count "
    ${STM32CP_CLI} -c port=${PORT} ${MODE} ${ERASE} -q -d ${FILEPATH} ${ADDRESS} ${OPTS}
    STATUS=$?
    sleep 0.5
  done
}

# Main
check_tool

if [ $# -lt 2 ]; then
    echo "Not enough arguments!"
    usage 2
fi

# Parse options
PROTOCOL=$1
FILEPATH=$2
# Protocol $1
# 1x: Erase all sectors
if [ $1 -ge 10 ]; then
  ERASE='-e all'
  PROTOCOL=$(($1 - 10))
fi

# Check if serial port option available
if [ $# -gt 2 ] && [[ $3 == "-serport="* ]]; then
  SERPORT=`echo $3 | cut -d'=' -f2`
  if [ ! -z $SERPORT ] && [[ $SERPORT != "/dev/"* ]]; then
    SERPORT="/dev/"${SERPORT}
  fi
fi

# Protocol $1
# 0: SWD
# 1: Serial
# 2: DFU
case $PROTOCOL in
  0)
    PORT='SWD'
    MODE='mode=UR';;
  1)
    if [ -z $SERPORT ]; then
      echo "Missing Serial port!"
      usage 3
    fi
    PORT=$SERPORT;;
  2)
    PORT='USB1'
    bootloaderMode;;
  *)
    echo "Protocol unknown!"
    usage 4;;
esac

if [ -z $SERPORT ]; then
  shift 2
else
  shift 3
fi

if [ $# -gt 0 ]; then
  OPTS="$@"
fi

upload

if [ ! -z $SERPORT ] && [ $STATUS -eq 0 ]; then
  echo -n "Waiting for $SERPORT serial..."
  count=0
  while [ ! -c $SERPORT ] && ((count++ < 40)); do
    sleep 0.1
  done
  count=0
  res=1
  while [ $res -ne 0 ] && ((count++ < 20)); do
    stty -F $SERPORT > /dev/null 2>&1
    res=$?
    sleep 1
  done
  echo "done"
fi

exit $STATUS

