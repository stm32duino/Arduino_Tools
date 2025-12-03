#!/bin/bash
#
# Clean built ARM64 binaries from linux-arm64/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/.."

echo "=========================================="
echo "Cleaning ARM64 Binaries"
echo "=========================================="
echo ""

# List of binaries to remove
BINARIES=(
    "dfu-util"
    "dfu-prefix"
    "dfu-suffix"
    "hid-flash"
    "upload_reset"
)

echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Check which binaries exist
FILES_TO_REMOVE=()
for binary in "${BINARIES[@]}"; do
    BINARY_PATH="${OUTPUT_DIR}/${binary}"
    if [ -f "${BINARY_PATH}" ]; then
        FILES_TO_REMOVE+=("${BINARY_PATH}")
    fi
done

# If no files to remove, exit
if [ ${#FILES_TO_REMOVE[@]} -eq 0 ]; then
    echo "No binaries found to remove."
    echo "Directory is already clean."
    exit 0
fi

# Show what will be removed
echo "The following binaries will be removed:"
for file in "${FILES_TO_REMOVE[@]}"; do
    echo "  - $(basename ${file})"
    if command -v file >/dev/null 2>&1; then
        file "${file}" | sed 's/^/    /'
    fi
done
echo ""

# Ask for confirmation if interactive
if [ -t 0 ]; then
    read -p "Continue? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Remove the binaries
echo "Removing binaries..."
for file in "${FILES_TO_REMOVE[@]}"; do
    rm -f "${file}"
    echo "  ✓ Removed $(basename ${file})"
done

echo ""
echo "=========================================="
echo "Clean completed successfully!"
echo "=========================================="
echo ""
echo "To rebuild the binaries, run:"
echo "  ./build.sh"
echo ""
