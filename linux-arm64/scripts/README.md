# ARM64 Linux Binary Build Scripts

This directory contains the build system for cross-compiling STM32 upload tools for ARM64 (aarch64) Linux platforms.

## Overview

These scripts use Docker to cross-compile the following binaries from x86_64 to ARM64:

- **dfu-util** - Device Firmware Update utility
- **dfu-prefix** - DFU file prefix tool
- **dfu-suffix** - DFU file suffix tool
- **hid-flash** - HID bootloader flash utility
- **upload_reset** - STM32 reset utility

## Prerequisites

- Docker installed and running
- Sufficient disk space (~2GB for build)

## Quick Start

From the repository root directory:

```bash
./linux-arm64/scripts/build.sh
```

This will:

1. Build and run ARM64 test stage (validates binaries work via QEMU on x86_64)
2. Build Docker image with the ARM64 cross-compilation toolchain
3. Compile all required binaries for ARM64
4. Extract the binaries to `linux-arm64/`
5. Set executable permissions
6. Copy additional files (udev rules, helper scripts)
7. Verify binary architecture
8. Clean up the Docker container

## Build Script Details

### `build.sh`

Main build orchestration script that performs the complete build and test workflow.

**What it does:**

1. **Validates prerequisites** - Checks Docker is installed and running
2. **Builds test stage** - Uses `docker buildx build --platform linux/arm64 --target test`
   - Cross-compiles binaries for ARM64
   - Tests all binaries on ARM64 (uses QEMU emulation on x86_64)
   - Ensures binaries actually execute correctly
   - Build fails if any binary doesn't work
3. **Builds export stage** - Uses `docker build` to create final image
4. **Extracts binaries** - Copies binaries from container to `linux-arm64/`
5. **Sets permissions** - Makes all binaries executable
6. **Copies additional files** - Copies udev rules and helper scripts from `linux/`
7. **Verifies output** - Runs `file` command to confirm ARM64 architecture

### `clean.sh`

Removes all built ARM64 binaries from the `linux-arm64/` directory.

### `Dockerfile`

Multi-stage Docker build with integrated testing.
