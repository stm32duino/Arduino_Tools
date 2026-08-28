# ARM64 Linux Binary Build Scripts

This directory contains the build system for cross-compiling STM32 upload tools for ARM64 (aarch64) Linux platforms.

## Overview

These scripts use Docker to cross-compile the following binaries from x86_64 to ARM64:

- **dfu-util** - Device Firmware Update utility
- **dfu-prefix** - DFU file prefix tool
- **dfu-suffix** - DFU file suffix tool
- **hid-flash** - HID bootloader flash utility
- **upload_reset** - STM32 reset utility
- **uf2upload** - CDC 1200-bps touch and UF2 mass-storage uploader

## Prerequisites

- Docker installed and running
- Sufficient disk space (~2GB for build)

## Quick Start

From the repository root directory:

```bash
./src/linux-aarch64/build.sh
```

This will:

1. Build and run ARM64 test stage (validates binaries work via QEMU on x86_64)
2. Build Docker image with the ARM64 cross-compilation toolchain
3. Compile all required binaries for ARM64
4. Extract the binaries to `linux/aarch64/`
5. Set executable permissions
6. Verify binary architecture
7. Clean up the Docker container

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
4. **Extracts binaries** - Copies binaries from container to `linux/aarch64/`
5. **Sets permissions** - Makes all binaries executable
6. **Verifies output** - Runs `file` command to confirm ARM64 architecture

### `clean.sh`

Removes all built ARM64 binaries from the `linux/aarch64/` directory.

### `Dockerfile`

Multi-stage Docker build with integrated testing.

## Build only `uf2upload`

For a local cross-build of just the UF2 uploader, install an AArch64 GNU C++
cross-compiler and run:

```bash
make -C src/uf2upload aarch64
file linux/aarch64/uf2upload
```

The resulting executable is for a Linux ARM64/AArch64 host, not for the STM32
target. See [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) for local cross-build and
QEMU validation steps, including their limitations.
