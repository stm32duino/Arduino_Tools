#!/bin/bash
set -o nounset                              # Treat unset variables as an error
#set -x
STM32CP_CLI=STM32_Programmer.sh
ADDRESS=0x8000000
FILEPATH=
MODE=
PORT=
OPTS=

###############################################################################
## Help function
usage()
{
  echo "############################################################"
  echo "##"
  echo "## `basename $0` <protocol> <file_path> [OPTIONS]"
  echo "##"
  echo "## protocol: "
  echo "##   0: SWD"
  echo "##   1: Serial "
  echo "##   2: DFU"
  echo "## file_path: file path name to be downloaded: (bin, hex)"
  echo "## Options:"
  echo "##   For SWD: -rst"
  echo "##     -rst: Reset system (default)"
  echo "##   For Serial: <com_port> -s"
  echo "##     com_port: serial identifier. Ex: /dev/ttyS0"
  echo "##     -s: start automatically"
  echo "##   For DFU: none"
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

check_tool

if [ $# -lt 2 ]; then
    echo "Not enough arguments!"
    usage 2
fi

FILEPATH=$2

# Parse options
# Protocol $1
# 0: SWD
# 1: Serial
# 2: DFU
case $1 in
  0)
    PORT='SWD'
    MODE='mode=UR'
    if [ $# -lt 3 ]; then
      OPTS=-rst
    else
      OPTS=$3
    fi;;
  1)
    if [ $# -lt 3 ]; then
      usage 3
    else
      PORT=$3
      if [ $# -gt 3 ]; then
        shift 3
        OPTS="$@"
      fi
    fi;;
  2)
    PORT='USB1';;
  *)
    echo "Protocol unknown!"
    usage 4;;
esac

${STM32CP_CLI} -c port=${PORT} ${MODE} -q -d ${FILEPATH} ${ADDRESS} ${OPTS}

exit 0
