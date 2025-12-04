#!/bin/bash
#
# Build script for ARM64 Linux binaries using Docker
# This script builds all necessary binaries and copies them to linux/aarch64/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/linux/aarch64"

echo "========================================"
echo "Building ARM64 binaries using Docker"
echo "========================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH" >&2
    echo "Please install Docker: https://docs.docker.com/get-docker/" >&2
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running" >&2
    echo "Please start Docker and try again" >&2
    exit 1
fi

echo "Step 1: Building Docker image and running tests..."
# Build with buildx to enable ARM64 test stage (requires QEMU on x86_64)
docker buildx build --platform linux/arm64 \
             --target test \
             -f "${SCRIPT_DIR}/Dockerfile" \
             -t arduino-tools-arm64-builder-test:latest \
             --load \
             "${REPO_ROOT}"

echo ""
echo "Step 2: Building export stage for binary extraction..."
docker build -f "${SCRIPT_DIR}/Dockerfile" \
             -t arduino-tools-arm64-builder:latest \
             "${REPO_ROOT}"

echo ""
echo "Step 3: Creating container to extract binaries..."
CONTAINER_ID=$(docker create arduino-tools-arm64-builder:latest)

echo ""
echo "Step 4: Extracting binaries to ${OUTPUT_DIR}..."
mkdir -p "${OUTPUT_DIR}"

# Copy binaries from container
docker cp "${CONTAINER_ID}:/dfu-util" "${OUTPUT_DIR}/"
docker cp "${CONTAINER_ID}:/dfu-prefix" "${OUTPUT_DIR}/"
docker cp "${CONTAINER_ID}:/dfu-suffix" "${OUTPUT_DIR}/"
docker cp "${CONTAINER_ID}:/hid-flash" "${OUTPUT_DIR}/"
docker cp "${CONTAINER_ID}:/upload_reset" "${OUTPUT_DIR}/"

echo ""
echo "Step 5: Cleaning up container..."
docker rm "${CONTAINER_ID}" > /dev/null

echo ""
echo "Step 6: Setting executable permissions..."
chmod +x "${OUTPUT_DIR}/dfu-util"
chmod +x "${OUTPUT_DIR}/dfu-prefix"
chmod +x "${OUTPUT_DIR}/dfu-suffix"
chmod +x "${OUTPUT_DIR}/hid-flash"
chmod +x "${OUTPUT_DIR}/upload_reset"

echo ""
echo "Step 7: Verifying built binaries..."
echo "----------------------------------------"
file "${OUTPUT_DIR}/dfu-util"
file "${OUTPUT_DIR}/dfu-prefix"
file "${OUTPUT_DIR}/dfu-suffix"
file "${OUTPUT_DIR}/hid-flash"
file "${OUTPUT_DIR}/upload_reset"
echo "----------------------------------------"

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "ARM64 binaries are now available in: ${OUTPUT_DIR}/"
echo ""
echo "All required binaries have been built:"
echo "  - dfu-util, dfu-prefix, dfu-suffix (DFU programming)"
echo "  - hid-flash (HID bootloader)"
echo "  - upload_reset (Reset utility)"
echo ""
echo "Files in ${OUTPUT_DIR}:"
ls -lh "${OUTPUT_DIR}"
