#!/bin/sh -
set -o nounset # Treat unset variables as an error
# set -o xtrace  # Print command traces before executing command.

UNAME_OS="$(uname -s)"
GNU_GETOPT="n" # "y" if GNU getopt is available
STM32CP_CLI=
INTERFACE=
PORT=
FILEPATH=
OFFSET=0x0
# Optional
ADDRESS=0x8000000
START=0x8000000
ERASE=
# Optional for SWD
FREQ=
MODE=UR
SERIAL_NUMBER=
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
    -b, --bin <file_path>                    binary file path to be downloaded: bin or hex
  Optional options:
    -a, --address <hex value>                flash base address. Default: $ADDRESS
    -e, --erase                              erase all sectors before flashing
    -s, --start <hex value>                  start address after flashing. Default: $START
    -o, --offset <hex value>                 offset from flash base ($ADDRESS) where flashing should start

  Specific options for SWD protocol:
    Optional:
      -f, --freq <value>                     SWD frequency in KHz.
      -m, --mode                             connection mode: UR (default), HOTPLUG, POWERDOWN or hwRstPulse
      -n, --snum <serial number>             serial number of the ST-Link device (if multiple ST-Link devices are connected)
  Specific options for Serial protocol:
    Mandatory:
      -c, --com <name>                       serial identifier, ex: COM1 or /dev/ttyS0,...
    Optional:
      -d, --dtr <low/high>                   polarity of DTR signal
      -p, --parity <none/even/odd>           parity bit configuration ('even' by default)
      -r, --rts <low/high>                   polarity of RTS signal ('low' by default)

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

check_getopt() {
  case "${UNAME_OS}" in
    Linux* | Windows*)
      GNU_GETOPT="y"
      ;;
    Darwin*)
      # Check if getopt is in the path and if it is gnu or BSD version in the path
      if command -v getopt >/dev/null 2>&1; then
        getopt --test >/dev/null 2>&1
        if [ $? -eq 4 ]; then
          GNU_GETOPT="y"
        fi
      fi
      # If getopt is not gnu version, check if it is installed via brew
      if [ "${GNU_GETOPT}" != "y" ]; then
        if command -v brew >/dev/null 2>&1; then
          BREW_PREFIX=$(brew --prefix)
          if command -v "${BREW_PREFIX}/bin/getopt" >/dev/null 2>&1; then
            "${BREW_PREFIX}"/bin/getopt --test >/dev/null 2>&1
            if [ $? -eq 4 ]; then
              export PATH="${BREW_PREFIX}/bin:$PATH"
              GNU_GETOPT="y"
            fi
          fi
          if [ "${GNU_GETOPT}" != "y" ]; then
            if command -v "${BREW_PREFIX}/opt/gnu-getopt/bin/getopt" >/dev/null 2>&1; then
              export PATH="${BREW_PREFIX}/opt/gnu-getopt/bin":"$PATH"
              GNU_GETOPT="y"
            fi
          fi
        fi
        # Check for MacPorts getopt
        if [ "${GNU_GETOPT}" != "y" ]; then
          if command -v /opt/local/bin/getopt >/dev/null 2>&1; then
            /opt/local/bin/getopt --test >/dev/null 2>&1
            if [ $? -eq 4 ]; then
              export PATH="/opt/local/bin:$PATH"
              GNU_GETOPT="y"
            fi
          fi
        fi
        # Fallback to previous check
        if [ "${GNU_GETOPT}" != "y" ]; then
          if ! command -v /usr/local/opt/gnu-getopt/bin/getopt >/dev/null 2>&1; then
            if command -v /opt/homebrew/opt/gnu-getopt/bin/getopt >/dev/null 2>&1; then
              export PATH="/opt/homebrew/opt/gnu-getopt/bin":"$PATH"
              GNU_GETOPT="y"
            fi
          else
            export PATH="/usr/local/opt/gnu-getopt/bin":"$PATH"
            GNU_GETOPT="y"
          fi
        fi
      fi
      ;;
    *)
      echo "Unknown host OS: ${UNAME_OS}." >&2
      exit 1
      ;;
  esac
}

# Qt in STM32CubeProgrammer expects a UTF-8 locale on Linux/macOS.
ensure_utf8_locale() {
  case "${UNAME_OS}" in
    Linux* | Darwin*)
      if command -v locale >/dev/null 2>&1; then
        CHARMAP=$(LC_ALL='' LANG='' locale charmap 2>/dev/null || true)
        case "${CHARMAP}" in
          UTF-8 | utf8) ;;
          *)
            LOCALES_RES=$(locale -a 2>/dev/null || true)
            if printf '%s\n' "${LOCALES_RES}" | grep -qi '^C\.UTF-8$'; then
              export LANG=C.UTF-8
              export LC_ALL=C.UTF-8
            elif printf '%s\n' "${LOCALES_RES}" | grep -qiE '^en_US\.(UTF-8|utf8)$'; then
              export LANG=en_US.UTF-8
              export LC_ALL=en_US.UTF-8
            fi
            ;;
        esac
      fi
      ;;
  esac
}

check_getopt
ensure_utf8_locale

# Check STM32CubeProgrammer cli availability
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
if [ "${GNU_GETOPT}" = "y" ]; then
  if ! options=$(getopt -a -o hi:b:a:es:o:f:m:n:c:d:p:r:v: --long help,interface:,bin:,address:,erase,start:,offset:,freq:,mode:,snum:,com:,dtr:,parity:,rts:,pid:,vid: -- "$@"); then
    echo "Terminating..." >&2
    exit 1
  fi
else
  echo "Warning: long options not supported due to getopt from FreeBSD usage."
  echo "         Space in arguments is not supported."
  if ! options=$(getopt hi:b:a:es:o:f:m:n:c:d:p:r:v: "$@"); then
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
    -b | --bin)
      FILEPATH=$2
      shift 2
      ;;
    -a | --address)
      ADDRESS=$2
      shift 2
      ;;
    -e | --erase)
      ERASE="--erase all"
      shift 1
      ;;
    -s | --start)
      START=$2
      shift 2
      ;;
    -o | --offset)
      OFFSET=$2
      shift 2
      ;;
    -f | --freq)
      FREQ=$2
      shift 2
      ;;
    -m | --mode)
      MODE=$2
      shift 2
      ;;
    -n | --snum)
      SERIAL_NUMBER="$2"
      shift 2
      ;;
    -c | --com)
      PORT=$2
      shift 2
      ;;
    -d | --dtr)
      DTR=$(echo "dtr=$2" | tr '[:upper:]' '[:lower:]')
      shift 2
      ;;
    -p | --pid | --parity)
      PID=$2
      PARITY=$(echo "$2" | tr '[:lower:]' '[:upper:]')
      shift 2
      ;;
    -r | --rts)
      RTS=$(echo "rts=$2" | tr '[:upper:]' '[:lower:]')
      shift 2
      ;;
    -v | --vid)
      VID=$2
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
  echo "Error missing binary file argument!" >&2
  usage 1
fi
if [ ! -r "${FILEPATH}" ]; then
  echo "Error ${FILEPATH} does not exist!" >&2
  usage 1
fi

case "${INTERFACE}" in
  swd)
    PORT_PARAM="port=SWD"
    if [ -n "${FREQ}" ]; then
      case "${FREQ}" in
        0) ;;
        *[!0-9]*)
          echo "Invalid SWD frequency (expected integer KHz): ${FREQ}" >&2
          exit 1
          ;;
        *)
          PORT_PARAM="${PORT_PARAM} freq=${FREQ}"
          ;;
      esac
    fi
    if [ -n "${SERIAL_NUMBER}" ] && [ "${SERIAL_NUMBER}" != "0" ]; then
      PORT_PARAM="${PORT_PARAM} sn=${SERIAL_NUMBER}"
    fi
    ${STM32CP_CLI} --connect "${PORT_PARAM}" mode="${MODE}" "${ERASE}" --quietMode --download "${FILEPATH}" "${ADDRESS}" --start "${START}"
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
