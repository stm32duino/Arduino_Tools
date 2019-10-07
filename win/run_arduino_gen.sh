#!/bin/sh -

set -e

REMOTEPROC_DIR="/sys/class/remoteproc/remoteproc0"
ELF_NAME="arduino.ino.elf"
ELF_INSTALL_PATH="/lib/firmware/$ELF_NAME"
INSTALL_PATH="/usr/local/arduino/run_arduino.sh"
# systemd path should be same as ${systemd_unitdir}/system/ in the yoctdo distro
SYSTEMD_SERVICE_PATH="/lib/systemd/system/$(basename $INSTALL_PATH .sh).service"
# Will be defined in autodetect_board()
BOARD=""

# A pair of prenthesis+percent is used as placeholder.
### {% BEGINNING OF BINARY PART ###
ELF_HASH=""
ELF_BINARY=""
### END OF BINARY PART %} ###


autodetect_board() {
  if [ ! -d /proc/device-tree/ ]; then
    echo "Proc Device tree are not available, Could not detect on which board we are" > /dev/kmsg
    exit 1
  fi

  #search on device tree compatible entry the board type
  if $(grep -q "stm32mp157c-ev" /proc/device-tree/compatible) ; then
    BOARD="STM32MP15_M4_EVAL"
  elif $(grep -q "stm32mp157c-dk" /proc/device-tree/compatible) ; then
    BOARD="STM32MP15_M4_DISCO"
  else
    echo "Board is not an EVAL or a DISCO BOARD" > /dev/kmsg
    exit 1
  fi
}


firmware_load() {
  if [ -z "$ELF_BINARY" ]; then
    echo "No Arduino binary contained. Run generate command first."
    exit 1
  fi

  if ( echo "$ELF_HASH $ELF_INSTALL_PATH" | sha256sum --status -c - 2>/dev/null ); then
    # The same firmware already exists, skip this step
    echo "The same firmware is already installed. Starting..."
    return 0
  fi

  # Decode base64-encoded binary to a temp directory and check hash
  tmp_elf_file="/tmp/$ELF_NAME"
  if which uudecode >/dev/null 2>&1; then
    echo -n "$ELF_BINARY" | uudecode -o /dev/stdout | gzip -d > "$tmp_elf_file"
  else 
    echo -n "$ELF_BINARY" | tail -n +2 | base64 -d - 2>/dev/null | gzip -d > "$tmp_elf_file"
  fi
  echo "$ELF_HASH $tmp_elf_file" | sha256sum --status -c -
  
  # Copy elf into /lib/firmware
  mv $tmp_elf_file $ELF_INSTALL_PATH
  echo "Arduino: Executable created: $ELF_INSTALL_PATH" > /dev/kmsg
}


firmware_start() {
  # Change the name of the firmware
  echo -n arduino.ino.elf > $REMOTEPROC_DIR/firmware

  # Change path to found firmware
  #echo -n /home/root >/sys/module/firmware_class/parameters/path

  # Restart firmware
  echo "Arduino: Starting $ELF_INSTALL_PATH" > /dev/kmsg
  echo start > $REMOTEPROC_DIR/state 2>/dev/null || true
}


firmware_stop() {
  # Stop the firmware
  echo "Arduino: Stopping $ELF_INSTALL_PATH" > /dev/kmsg
  echo stop > $REMOTEPROC_DIR/state 2>/dev/null || true
}


generate_packaged_script() {
  elf_path="$1"
  this_script=$(readlink -f "$0")
  output_script="$2"
  if [ "$this_script" = "$output_script" ]; then
    echo "The output file name must be diffent from this script file"
    exit 1
  fi
  
  # Generate a copy of this script with a self-contained elf binary and its hash
  # The elf binary is gzip'ed, making its size to 1/6, and then Base64-encoded
  # using uuencode.
  head -n $(grep -n "{%" "$this_script" | cut -d: -f1 | head -n 1) $this_script > $output_script 
  echo "ELF_HASH='$(sha256sum $elf_path | cut -d' ' -f1)'" >> $output_script
  echo -n "ELF_BINARY='" >> $output_script
  if which uuencode >/dev/null 2>&1; then
    gzip -c "$elf_path" | uuencode -m $ELF_NAME >> $output_script
  else
    echo "begin-base64 644 $ELF_NAME" >> $output_script
    gzip -c "$elf_path" | base64 >> $output_script
  fi
  echo "'" >> $output_script
  tail -n +$(grep -n "%}" "$this_script" | cut -d: -f1 | head -n 1) $this_script >> $output_script
}


systemd_install() {
  mkdir -p $(dirname $INSTALL_PATH)
  cp $0 "$INSTALL_PATH"
  echo "File created: $INSTALL_PATH"
  cat > "$SYSTEMD_SERVICE_PATH" << EOF
[Unit]
Description=Run Arduino firmware via remoteproc
After=systemd-modules-load.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=sh $INSTALL_PATH start
ExecStop=sh $INSTALL_PATH stop

[Install]
WantedBy=sysinit.target
EOF
  echo "File created: $SYSTEMD_SERVICE_PATH"
  echo "Please wait until systemd services are reloaded..."
  systemctl daemon-reload
  systemctl enable $(basename $SYSTEMD_SERVICE_PATH)
}


systemd_uninstall() {
  systemctl stop $(basename $SYSTEMD_SERVICE_PATH)
  systemctl disable $(basename $SYSTEMD_SERVICE_PATH)
  rm "$SYSTEMD_SERVICE_PATH"
  echo "File deleted: $SYSTEMD_SERVICE_PATH"
  rm -r $(dirname $INSTALL_PATH)
  echo "File deleted: $INSTALL_PATH"
}


case "$1" in
  start)
    autodetect_board
    firmware_load
    firmware_stop
    firmware_start
    ;;
  stop)
    autodetect_board
    firmware_stop
    ;;
  restart)
    autodetect_board
    firmware_stop
    firmware_start
    ;;
  install)
    autodetect_board
    systemd_install
    echo "Auto-start service $(basename $SYSTEMD_SERVICE_PATH) installed."
    ;;
  uninstall)
    autodetect_board
    systemd_uninstall
    echo "Auto-start service $(basename $SYSTEMD_SERVICE_PATH) uninstalled."
    ;;
  generate)
    generate_packaged_script $2 $3
    echo "$(readlink -f "$3") generated successfully."
    echo "This file should be uploaded manually by SCP, SFTP, Kermit, or etc."
    echo "Then run \"sh ./$(basename $3) start\" command in the board's console."
    echo "For detailed instructions, please visit:"
    echo "  https://github.com/stm32duino/Arduino_Core_STM32/tree/master/variants/STM32MP157_DK/README.md"
    ;;
  *)
    echo "Usage: $0 [start|stop|restart|generate|install|uninstall]"
    echo ""
    echo "run_arduino.sh is a helper script that helps managing an Arduino binary"
    echo "file for the coprocessor using remoteproc framework."
    echo ""
    echo "$0 generate <input ELF file> <output script file>"
    echo "    Generate a new shell script file that contains the input ELF binary."
    echo "    The contained ELF binary is gzip'ed and Base64-encoded by uuencode."
    echo ""
    echo "$0 start"
    echo "    Upload the binary to the coprocessor then start it."
    echo "    This command must be executed while the script contains the binary"
    echo "    after generate command is run."
    echo ""
    echo "$0 install"
    echo "    Run the binary on boot automatically by installing a systemd service."
    echo ""
    echo "$0 uninstall"
    echo "    Uninstall the autostart service."
    echo ""
    echo "$0 stop"
    echo "    Stop the coprocessor."
    echo ""
    echo "$0 restart"
    echo "    Restart the coprocessor."
    ;;
esac

exit 0
