# Local Linux ARM64 validation for `uf2upload`

## Scope

This document describes how to validate the Linux ARM64 (`aarch64`) host build
from an x86_64 Linux machine, including Ubuntu in WSL2. It is useful when an
ARM64 development board is not available.

The tested executable is `linux/aarch64/uf2upload`. It runs on a Linux ARM64
computer such as a Raspberry Pi 64-bit OS, ARM server, or ARM64 Linux VM; it
does **not** run on the STM32C5.

## What this can prove

- The source cross-compiles with the AArch64 GNU toolchain.
- The output is an AArch64 ELF and declares the expected Linux runtime
  dependencies.
- When run through QEMU user-mode emulation, the binary starts and its
  command-line, UF2 conversion, directory discovery, and file-copy paths work.

## What this cannot prove

- A physical ARM64 Linux host can enumerate the board's USB CDC and mass-storage
  interfaces.
- A real CDC 1200-bps request resets the board into TinyUF2.
- A real `XIAOC5BOOT` filesystem accepts the copied UF2 and programs flash.
- ARM32 (`armhf`) support. This document covers only 64-bit ARM (`aarch64`).

## Prerequisites on Ubuntu x86_64 / WSL2

```bash
sudo apt update
sudo apt install -y g++-aarch64-linux-gnu binutils-aarch64-linux-gnu \
  libc6-dev-arm64-cross file qemu-user-static xxd
```

`qemu-user-static` may register the ARM64 interpreter automatically through
`binfmt_misc`. If it does not, use `qemu-aarch64-static` explicitly as shown
below.

## Cross-build and inspect

From the Arduino_Tools repository root:

```bash
make -C src/uf2upload aarch64
file linux/aarch64/uf2upload
aarch64-linux-gnu-readelf -d linux/aarch64/uf2upload | grep NEEDED
```

Expected `file` output includes:

```text
ELF 64-bit ... ARM aarch64 ... interpreter /lib/ld-linux-aarch64.so.1
```

The binary is dynamically linked and normally needs the ARM64 Linux loader,
`libstdc++.so.6`, `libgcc_s.so.1`, and `libc.so.6` supplied by the eventual
ARM64 Linux distribution.

## QEMU execution with an ARM64 sysroot

Use the installed cross sysroot. The exact directory can vary; on Ubuntu it is
usually `/usr/aarch64-linux-gnu`.

```bash
sysroot=/usr/aarch64-linux-gnu
qemu-aarch64-static -L "$sysroot" linux/aarch64/uf2upload --help
```

This must print the uploader usage text and exit successfully.

## Simulated volume and UF2 conversion

`uf2upload` searches only `/Volumes`, `/media`, `/run/media`, and `/mnt` for
the volume label. Create an isolated test path under `/mnt`; do not point this
at a real bootloader volume.

```bash
set -eu

repo_root="$(git rev-parse --show-toplevel)"
work="$(mktemp -d)"
mount_root="/mnt/uf2upload-arm64-test-$$"
trap 'sudo rm -rf "$mount_root"; rm -rf "$work"' EXIT

printf '\\x01\\x02\\x03\\x04' > "$work/firmware.bin"
sudo mkdir -p "$mount_root/XIAOC5BOOT"
sudo chown -R "$(id -u):$(id -g)" "$mount_root"

qemu-aarch64-static -L /usr/aarch64-linux-gnu \
  "$repo_root/linux/aarch64/uf2upload" \
  --input "$work/firmware.bin" \
  --volume XIAOC5BOOT \
  --address 0x08008000 \
  --family 0x00C5C5C5 \
  --max-size 1015808 \
  --timeout 1000

test -f "$mount_root/XIAOC5BOOT"/*
stat -c '%n %s bytes' "$mount_root/XIAOC5BOOT"/*
xxd -g 4 -l 32 "$mount_root/XIAOC5BOOT"/*
```

For the 4-byte input, the copied UF2 must be 512 bytes. The first two words are
the UF2 magic values; the family field is `0x00C5C5C5` in little-endian order.

## Optional pseudo-terminal check

`socat` can provide a pseudo-terminal pair to exercise the Linux `termios`
1200-bps setup path. This is a code-path test only, not a USB CDC test. Arrange
for the simulated `XIAOC5BOOT` directory to appear while the uploader is
waiting, then pass one pseudo-terminal path through `--port`.

## Result wording

If every command above succeeds, use wording such as:

> The Linux ARM64 `uf2upload` binary was cross-built on Ubuntu x86_64 and
> executed under QEMU user-mode emulation. Command-line parsing, UF2 generation,
> simulated volume discovery, and file copy were validated. Physical ARM64 USB
> CDC and TinyUF2 hardware upload have not yet been validated.
