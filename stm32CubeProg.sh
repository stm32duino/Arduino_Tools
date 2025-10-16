#!/bin/sh -
set -o nounset # Treat unset variables as an error
# set -o xtrace  # Print command traces before executing command.

UNAME_OS="$(uname -s)"
GNU_GETOPT=
STM32CP_CLI=
INTERFACE=
PORT=
FILEPATH=
OFFSET=0x0
# Optional
ADDRESS=0x8000000
START=0x8000000
MODE=UR
ERASE=
# Optional for Serial
RTS=
DTR=
PARITY=EVEN
# Mandatory for DFU
VID=
PID=

###############################################################################
## Help function
usage() {
  echo "Usage: $(basename "$0") [OPTIONS]...

  Mandatory options:
    -i, --interface <'swd'/'dfu'/'serial'/'jlink'>   interface identifier: 'swd', 'dfu', 'serial' or 'jlink'
    -f, --file <path>                        file path to be downloaded: bin or hex
  Optional options:
    -a, --address <hex value>                flash base address. Default: $ADDRESS
    -e, --erase                              erase all sectors before flashing
    -m, --mode                               connection mode: UR (default), HOTPLUG, POWERDOWN or hwRstPulse
    -s, --start <hex value>                  start address after flashing. Default: $START
    -o, --offset <hex value>                 offset from flash base ($ADDRESS) where flashing should start

  Specific options for Serial protocol:
    Mandatory:
    -c, --com <name>                         serial identifier, ex: COM1 or /dev/ttyS0,...
    Optional:
      -r, --rts <low/high>                   polarity of RTS signal ('low' by default)
      -d, --dtr <low/high>                   polarity of DTR signal
      --parity <none/even/odd>         parity bit configuration ('even' by default)

  Specific options for DFU protocol:
    Mandatory:
      -v, --vid <hex value>                  vendor id, ex: 0x0483
      -p, --pid <hex value>                  product id, ex: 0xdf11

" >&2
  exit "$1"
}

aborting() {
  echo "STM32CubeProgrammer not found ($STM32CP_CLI).
  Please install it or add '<STM32CubeProgrammer path>/bin' to your PATH environment:
  https://www.st.com/en/development-tools/stm32cubeprog.html
  Aborting!" >&2
  exit 1
}

# Check STM32CubeProgrammer cli availability and getopt version
case "${UNAME_OS}" in
  Linux*)
    STM32CP_CLI=STM32_Programmer.sh
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      export PATH="$HOME/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      export PATH="/opt/stm32cubeprog/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      aborting
    fi
    ;;
  Darwin*)
    STM32CP_CLI=STM32_Programmer_CLI
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      export PATH="/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin":"$PATH"
    fi
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      aborting
    fi
    if ! command -v /usr/local/opt/gnu-getopt/bin/getopt >/dev/null 2>&1; then
      if ! command -v /opt/homebrew/opt/gnu-getopt/bin/getopt >/dev/null 2>&1; then
        echo "Warning: long options not supported due to getopt from FreeBSD usage."
        GNU_GETOPT=n
      else
        export PATH="/opt/homebrew/opt/gnu-getopt/bin":"$PATH"
      fi
    else
      export PATH="/usr/local/opt/gnu-getopt/bin":"$PATH"
    fi
    ;;
  Windows*)
    STM32CP_CLI=STM32_Programmer_CLI.exe
    if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
      if [ -n "${PROGRAMFILES+x}" ]; then
        STM32CP86=${PROGRAMFILES}/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin
        export PATH="${STM32CP86}":"$PATH"
      fi
      if [ -n "${PROGRAMW6432+x}" ]; then
        STM32CP=${PROGRAMW6432}/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin
        export PATH="${STM32CP}":"$PATH"
      fi
      if ! command -v $STM32CP_CLI >/dev/null 2>&1; then
        aborting
      fi
    fi
    ;;
  *)
    echo "Unknown host OS: ${UNAME_OS}." >&2
    exit 1
    ;;
esac

# parse command line arguments
# options may be followed by one colon to indicate they have a required arg
if [ -n "${GNU_GETOPT}" ]; then
  if ! options=$(getopt hi:ef:o:c:r:d:v:p: "$@"); then
    echo "Terminating..." >&2
    exit 1
  fi
else
  if ! options=$(getopt -a -o a:hi:m:ef:o:c:r:s:d:v:p: --long address:,help,interface:,mode:,erase,file:,start:,offset:,com:,rts:,dtr:,vid:,pid:,parity: -- "$@"); then
    echo "Terminating..." >&2
    exit 1
  fi
fi

eval set -- "$options"

while true; do
  case "$1" in
    -h | --help | -\?)
      usage 0
      ;;
    -i | --interface)
      INTERFACE=$(echo "$2" | tr '[:upper:]' '[:lower:]')
      echo "Selected interface: $INTERFACE"
      shift 2
      ;;
    -m | --mode)
      MODE=$2
      shift 2
      ;;
    -a | --address)
      ADDRESS=$2
      shift 2
      ;;
    -s | --start)
      START=$2
      shift 2
      ;;
    -e | --erase)
      ERASE="--erase all"
      shift 1
      ;;
    -f | --file)
      FILEPATH=$2
      shift 2
      ;;
    -o | --offset)
      OFFSET=$2
      shift 2
      ;;
    -c | --com)
      PORT=$2
      shift 2
      ;;
    -r | --rts)
      RTS=$(echo "rts=$2" | tr '[:upper:]' '[:lower:]')
      shift 2
      ;;
    -d | --dtr)
      DTR=$(echo "dtr=$2" | tr '[:upper:]' '[:lower:]')
      shift 2
      ;;
    -v | --vid)
      VID=$2
      shift 2
      ;;
    -p | --pid)
      PID=$2
      shift 2
      ;;
    --parity)
      PARITY=$(echo "$2" | tr '[:lower:]' '[:upper:]')
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown option $1"
      usage 1
      ;;
  esac
done

ADDRESS=$(printf "0x%x" $((ADDRESS + OFFSET)))

# Check mandatory options
if [ -z "${INTERFACE}" ]; then
  echo "Error missing interface!" >&2
  usage 1
fi
if [ -z "${FILEPATH}" ]; then
  echo "Error missing file argmument!" >&2
  usage 1
fi
if [ ! -r "${FILEPATH}" ]; then
  echo "Error ${FILEPATH} does not exist!" >&2
  usage 1
fi

case "${INTERFACE}" in
  swd)
    ${STM32CP_CLI} --connect port=SWD mode="${MODE}" "${ERASE}" --quietMode --download "${FILEPATH}" "${ADDRESS}" --start "${START}"
    ;;
  dfu)
    if [ -z "${VID}" ] || [ -z "${PID}" ]; then
      echo "Missing mandatory arguments for DFU mode (VID/PID)!" >&2
      exit 1
    fi
    ${STM32CP_CLI} --connect port=usb1 VID="${VID}" PID="${PID}" "${ERASE}" --quietMode --download "${FILEPATH}" "${ADDRESS}" --start "${START}"
    ;;
  serial)
    if [ -z "${PORT}" ]; then
      echo "Missing mandatory arguments for serial mode: serial identifier!" >&2
      exit 1
    fi
    if [ -n "${RTS}" ]; then
      if [ "${RTS}" != "rts=low" ] && [ "${RTS}" != "rts=high" ]; then
        echo "Wrong rts value waiting high or low instead of ${RTS}" >&2
        exit 1
      fi
    fi
    if [ -n "${DTR}" ]; then
      if [ "${DTR}" != "dtr=low" ] && [ "${DTR}" != "dtr=high" ]; then
        echo "Wrong dtr value waiting high or low instead of ${DTR}" >&2
        exit 1
      fi
    fi
    if [ "$PARITY" != "NONE" ] && [ "$PARITY" != "EVEN" ] && [ "$PARITY" != "ODD" ]; then
      echo "Wrong parity value waiting none, even or odd instead of ${PARITY}" >&2
      exit 1
    fi
    ${STM32CP_CLI} --connect port="${PORT}" P="${PARITY}" "${RTS}" "${DTR}" "${ERASE}" --quietMode --download "${FILEPATH}" "${ADDRESS}" --start "${START}"
    ;;
  jlink)
    ${STM32CP_CLI} --connect port=JLINK ap=0 "${ERASE}" --quietMode --download "${FILEPATH}" "${ADDRESS}" --start "${START}"
    ;;
  *)
    echo "Protocol unknown!" >&2
    usage 4
    ;;
esac

exit $?
