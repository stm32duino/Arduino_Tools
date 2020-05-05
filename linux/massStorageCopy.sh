#!/bin/bash
set -o nounset # Treat unset variables as an error

# List
bin_filepath=
mountpoint_name=
mountpoint_path=

###############################################################################
## Help function
usage() {
  echo "############################################################"
  echo "##"
  echo "## $(basename "$0") [-I <filepath>] [-O <mountpoint(s)> ]"
  echo "##"
  echo "## Options:"
  echo "##   -I: filepath binary to copy"
  echo "##   -O: mountpoint(s) destination name"
  echo "##     Could be a list (separated by','). Ex: \"NODE_1,NODE2,NODE_3\""
  echo "## Note:"
  echo "##   -I and -O are optionals and kept for backward compatibility."
  echo "############################################################"
  exit 0
}

if [ $# -lt 2 ]; then
  usage
  exit 1
fi

# Parsing options
if [ "$1" == "-I" ]; then
  shift 1
fi

bin_filepath=$1

if [ "$2" == "-O" ]; then
  shift 1
fi
# Strip first and last ""
mountpoint_name="${2%\"}"
mountpoint_name="${mountpoint_name#\"}"

if [ -z "$bin_filepath" ]; then
  echo "No binary file path provided!"
  exit 1
fi
if [ -z "$mountpoint_name" ]; then
  echo "No mountpoint name provided!"
  exit 1
fi

if [ ! -f "$bin_filepath" ]; then
  echo "$bin_filepath not found!"
  exit 2
fi

# Add short node name
IFS=' ,\t' read -ra mnt_list <<< "$mountpoint_name"
for mnt in "${mnt_list[@]}"; do
  if [[ "$mnt" == "NODE_"* ]]; then
    mountpoint_name="${mountpoint_name},${mnt//E_/_}"
  fi
done

# Search the mountpoint
IFS=' ,\t' read -ra mnt_list <<< "$mountpoint_name"
for mnt in "${mnt_list[@]}"; do
  # mnt_path_list=(`cat /proc/mounts | cut -d' ' -f2 | sort -u | grep $mnt`)
  mnt_path_list=($(df -Hl | grep -v "Mounted on" | rev | cut -d' ' -f1 | rev | sort -u | grep "$mnt"))
  if [ ${#mnt_path_list[@]} -ne 0 ]; then
    # Ensure to have exact match
    for mnt_path in "${mnt_path_list[@]}"; do
      mnt_name=$(echo "$mnt_path" | rev | cut -d'/' -f1 | rev)
      if [ "$mnt_name" = "$mnt" ]; then
        echo "Found '$mnt' at '$mnt_path'"
        mountpoint_path=$mnt_path
        break
      fi
    done
  fi
done

if [ -z "$mountpoint_path" ] || [ ! -d "$mountpoint_path" ]; then
  echo "$mountpoint_name not found."
  echo "Please ensure the device is correctly connected and mounted."
  exit 3
fi

# Copy the binary to the mountpoint
echo "Copying $bin_filepath to $mountpoint_path..."
cp "$bin_filepath" "$mountpoint_path"

exit $?
