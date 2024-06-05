#!/bin/sh -
set -o nounset # Treat unset variables as an error
# set -o xtrace # Print command traces before executing command.

STM32CP_CLI=
ADDRESS=0x8000000
ERASE=""
MODE=""
PORT=""
OPTS=""

###############################################################################
## Help function
usage() {
  echo "############################################################"
  echo "##"
  echo "## $(basename "$0") <protocol> <file_path> <offset> [OPTIONS]"
  echo "##"
  echo "## protocol:"
  echo "##   0: SWD"
  echo "##   1: Serial"
  echo "##   2: DFU"
  echo "##   Note: prefix it by 1 to erase all sectors."
  echo "##         Ex: 10 erase all sectors using SWD interface."
  echo "## file_path: file path name to be downloaded: (bin, hex)"
  echo "## offset: offset to add to $ADDRESS"
  echo "## Options:"
  echo "##   For SWD and DFU: no mandatory options"
  echo "##   For Serial: <com_port>"
  echo "##     com_port: serial identifier (mandatory). Ex: /dev/ttyS0 or COM1"
  echo "##"
  echo "## Note: all trailing arguments will be passed to the $STM32CP_CLI"
  echo "##   They have to be valid commands for STM32CubeProgrammer cli"
  echo "##   Ex: -rst: Reset system"
  echo "############################################################"
  exit "$1"
}

UNAME_OS="$(uname -s)"
case "${UNAME_OS}" in
  Linux*)
    STM32CP_CLI=STM32_Programmer.sh
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      export PATH="$HOME/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      export PATH="/opt/stm32cubeprog/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      echo "STM32CubeProgrammer not found ($STM32CP_CLI)."
      echo "Please install it or add '<STM32CubeProgrammer path>/bin' to your PATH environment:"
      echo "https://www.st.com/en/development-tools/stm32cubeprog.html"
      echo "Aborting!"
      exit 1
    fi
    ;;
  Darwin*)
    STM32CP_CLI=STM32_Programmer_CLI
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      export PATH="/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      echo "STM32CubeProgrammer not found ($STM32CP_CLI)."
      echo "Please install it or add '<STM32CubeProgrammer path>/bin' to your PATH environment:"
      echo "https://www.st.com/en/development-tools/stm32cubeprog.html"
      echo "Aborting!"
      exit 1
    fi
    ;;
  Windows*)
    STM32CP_CLI=STM32_Programmer_CLI.exe
    if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
      if [ -n "${PROGRAMFILES+x}" ]; then
        STM32CP86=${PROGRAMFILES}/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin
        export PATH="${STM32CP86}":"$PATH"
      fi
      if [ -n "${PROGRAMW6432+x}" ]; then
        STM32CP=${PROGRAMW6432}/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin
        export PATH="${STM32CP}":"$PATH"
      fi
      if ! command -v $STM32CP_CLI > /dev/null 2>&1; then
        echo "STM32CubeProgrammer not found ($STM32CP_CLI)."
        echo "Please install it or add '<STM32CubeProgrammer path>\bin' to your PATH environment:"
        echo "https://www.st.com/en/development-tools/stm32cubeprog.html"
        echo "Aborting!"
      fi
    fi
    ;;
  *)
    echo "Unknown host OS: ${UNAME_OS}."
    exit 1
    ;;
esac

if [ $# -lt 3 ]; then
  echo "Not enough arguments!"
  usage 2
fi

# Parse options
PROTOCOL=$1
FILEPATH=$2
OFFSET=$3
ADDRESS=$(printf "0x%x" $((ADDRESS + OFFSET)))

# Protocol $1
# 1x: Erase all sectors
if [ "$1" -ge 10 ]; then
  ERASE="yes"
  PROTOCOL=$(($1 - 10))
fi
# Protocol $1
# 0: SWD
# 1: Serial
# 2: DFU
case $PROTOCOL in
  0)
    PORT="SWD"
    MODE="mode=UR"
    shift 3
    ;;
  1)
    if [ $# -lt 4 ]; then
      usage 3
    else
      PORT=$4
      shift 4
    fi
    ;;
  2)
    PORT="USB1"
    ERASE="yes"
    shift 3
    ;;
  *)
    echo "Protocol unknown!"
    usage 4
    ;;
esac

if [ $# -gt 0 ]; then
  OPTS="$*"
fi

${STM32CP_CLI} -c port=${PORT} ${MODE} ${ERASE:+"-e all"} -q -d "${FILEPATH}" "${ADDRESS}" -s "${ADDRESS}" "${OPTS}"

exit $?
