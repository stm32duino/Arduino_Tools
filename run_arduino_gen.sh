#!/bin/sh -

set -e

REMOTEPROC_DIR="/sys/class/remoteproc/remoteproc0"
RPMSG_DIR="/dev/ttyRPMSG0"
ELF_NAME="arduino.ino.elf"
ELF_INSTALL_PATH="/lib/firmware/$ELF_NAME"
INSTALL_PATH="/usr/local/arduino/run_arduino.sh"
# systemd path should be same as ${systemd_unitdir}/system/ in the yocto distro
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
  if grep -q "stm32mp157c-ev" /proc/device-tree/compatible; then
    BOARD="STM32MP157_EVAL"
  elif grep -q "stm32mp157c-dk" /proc/device-tree/compatible; then
    BOARD="STM32MP157_DK"
  elif grep -q "stm32mp157a-dk" /proc/device-tree/compatible; then
    BOARD="STM32MP157_DK"
  elif grep -q "stm32mp157" /proc/device-tree/compatible; then
    BOARD="STM32MP157_GENERIC"
  else
    echo "Board is not an STM32MP157 BOARD" > /dev/kmsg
    exit 1
  fi
  echo "Board is $BOARD" > /dev/kmsg
}

firmware_load() {
  if [ -z "$ELF_BINARY" ]; then
    echo "No Arduino binary contained. Run generate command first."
    exit 1
  fi

  if (echo "$ELF_HASH $ELF_INSTALL_PATH" | sha256sum --status -c - 2> /dev/null); then
    # The same firmware already exists, skip this step
    echo "The same firmware is already installed. Starting..."
    return 0
  fi

  # Decode base64-encoded binary to a temp directory and check hash
  tmp_elf_file="/tmp/$ELF_NAME"
  if which uudecode > /dev/null 2>&1; then
    printf "%s" "$ELF_BINARY" | uudecode -o /dev/stdout | gzip -d > "$tmp_elf_file"
  else
    printf "%s" "$ELF_BINARY" | tail -n +2 | base64 -d - 2> /dev/null | gzip -d > "$tmp_elf_file"
  fi
  echo "$ELF_HASH $tmp_elf_file" | sha256sum --status -c -

  # Copy elf into /lib/firmware
  mv $tmp_elf_file $ELF_INSTALL_PATH
  echo "Arduino: Executable created: $ELF_INSTALL_PATH" > /dev/kmsg
}

firmware_start() {
  # Change the name of the firmware
  printf arduino.ino.elf > $REMOTEPROC_DIR/firmware

  # Change path to found firmware
  #printf /home/root >/sys/module/firmware_class/parameters/path

  # Restart firmware
  echo "Arduino: Starting $ELF_INSTALL_PATH" > /dev/kmsg
  echo start > $REMOTEPROC_DIR/state 2> /dev/null || true
}

firmware_stop() {
  # Stop the firmware
  echo "Arduino: Stopping $ELF_INSTALL_PATH" > /dev/kmsg
  echo stop > $REMOTEPROC_DIR/state 2> /dev/null || true
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
  head -n "$(grep -n "{%" "$this_script" | cut -d: -f1 | head -n 1)" "$this_script" > "$output_script"
  echo "ELF_HASH='$(sha256sum "$elf_path" | cut -d' ' -f1)'" >> "$output_script"
  printf "ELF_BINARY='" >> "$output_script"
  if which uuencode > /dev/null 2>&1; then
    gzip -c "$elf_path" | uuencode -m $ELF_NAME >> "$output_script"
  else
    echo "begin-base64 644 $ELF_NAME" >> "$output_script"
    gzip -c "$elf_path" | base64 >> "$output_script"
  fi
  echo "'" >> "$output_script"
  tail -n +"$(grep -n "%}" "$this_script" | cut -d: -f1 | head -n 1)" "$this_script" >> "$output_script"
  dos2unix "$output_script" 2> /dev/null
}

systemd_install() {
  mkdir -p "$(dirname $INSTALL_PATH)"
  cp "$0" "$INSTALL_PATH"
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
  systemctl enable "$(basename "$SYSTEMD_SERVICE_PATH")"
}

systemd_uninstall() {
  systemctl stop "$(basename "$SYSTEMD_SERVICE_PATH")"
  systemctl disable "$(basename "$SYSTEMD_SERVICE_PATH")"
  rm "$SYSTEMD_SERVICE_PATH"
  echo "File deleted: $SYSTEMD_SERVICE_PATH"
  rm -r "$(dirname $INSTALL_PATH)"
  echo "File deleted: $INSTALL_PATH"
}

try_send() {
  # Wait for /dev/ttyRPMSGx for 5 seconds, because the virtual device can be
  # created later depending on where Serial.begin() is located in the Arduino code.
  count=0
  while [ ! -c $RPMSG_DIR ]; do
    if [ $count -eq 2 ]; then
      echo "Waiting for virtual serial $RPMSG_DIR is created..."
    elif [ $count -ge 5 ]; then
      echo "No virtual serial $RPMSG_DIR is created."
      echo "If you didn't enable the virtual serial, ignore this message."
      return 0
    fi
    sleep 1
    count=$((count + 1))
  done
  # Linux host must send any dummy data first to finish initialization of rpmsg
  # on the coprocessor side. This message should be discarded.
  # See: https://github.com/OpenAMP/open-amp/issues/182
  printf "DUMMY" > $RPMSG_DIR
  echo "Virtual serial $RPMSG_DIR connection established."
}

case "$1" in
  start)
    autodetect_board
    firmware_load
    firmware_stop
    firmware_start
    try_send
    echo "Arduino firmware started."
    ;;
  stop)
    autodetect_board
    firmware_stop
    echo "Arduino firmware stopped."
    ;;
  restart)
    autodetect_board
    firmware_stop
    firmware_start
    try_send
    echo "Arduino firmware restarted."
    ;;
  install)
    autodetect_board
    systemd_install
    echo "Auto-start service $(basename "$SYSTEMD_SERVICE_PATH") installed."
    ;;
  uninstall)
    autodetect_board
    systemd_uninstall
    echo "Auto-start service $(basename "$SYSTEMD_SERVICE_PATH") uninstalled."
    ;;
  monitor)
    autodetect_board
    stty raw -echo -echoe -echok -F $RPMSG_DIR
    cat $RPMSG_DIR
    ;;
  send-msg)
    autodetect_board
    echo "${@:2}" > $RPMSG_DIR
    ;;
  send-file)
    autodetect_board
    # Maximum buffer size at a time: 512 - 16 bytes
    # Otherwise, it used to return error in earlier version of OpenSTLinux
    # Reference: https://elixir.bootlin.com/linux/v5.5.6/source/drivers/rpmsg/virtio_rpmsg_bus.c#L581
    dd if="$2" bs=496 of=$RPMSG_DIR
    ;;
  log)
    cat /sys/kernel/debug/remoteproc/remoteproc0/trace0
    ;;
  minicom)
    autodetect_board
    TERM=xterm minicom -D $RPMSG_DIR
    ;;
  generate)
    output=$(echo "$3" | sed 's/\.ino\././g')
    generate_packaged_script "$2" "$output"
    echo "$(readlink -f "$output") generated successfully."
    echo "This file should be uploaded manually by SCP, SFTP, Kermit, or etc."
    echo "Then run \"sh ./$(basename "$output") start\" command in the board's console."
    echo "For detailed instructions, please visit:"
    echo "  https://github.com/stm32duino/Arduino_Core_STM32/tree/master/variants/STM32MP157_DK/README.md"
    ;;
  *)
    echo "Usage: $0 [start|stop|restart]"
    echo "       $0 [install|uninstall]"
    echo "       $0 [monitor|minicom|log]"
    echo "       $0 [send-msg|send-file] ..."
    echo "       $0 [generate]"
    echo ""
    echo "$0 is a helper script that helps managing an Arduino binary"
    echo "file for the coprocessor using remoteproc framework."
    echo ""
    echo "$0 generate <input ELF file> <output script file>"
    echo "    For Arduino IDE internal use only."
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
    echo "$0 monitor"
    echo "    Monitor data received from the coprocessor via RPMsg serial (VirtIOSerial)."
    echo "    This command cannot send any data to the coprocessor."
    echo ""
    echo "$0 send-msg <message...>"
    echo "    Send a message to the coprocessor via RPMsg serial (VirtIOSerial)."
    echo ""
    echo "$0 send-file <filename>"
    echo "    Send a file content to the coprocessor via RPMsg serial (VirtIOSerial)."
    echo ""
    echo "$0 minicom"
    echo "    Launch minicom interactive serial communication program."
    echo ""
    echo "$0 log"
    echo "    Print debugging log in OpenAMP trace buffer."
    echo ""
    echo "$0 stop"
    echo "    Stop the coprocessor."
    echo ""
    echo "$0 restart"
    echo "    Restart the coprocessor."
    ;;
esac

exit 0
