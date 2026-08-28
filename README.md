# Arduino_Tools
[![GitHub release](https://img.shields.io/github/release/stm32duino/Arduino_Tools.svg)](https://github.com/stm32duino/Arduino_Tools/releases/latest)
[![GitHub commits](https://img.shields.io/github/commits-since/stm32duino/Arduino_Tools/2.5.0.svg)](https://github.com/stm32duino/Arduino_Tools/compare/2.4.0...main)

Contains upload tools for STM32 based boards and some other usefull scripts.

## UF2 uploader

`uf2upload` is a self-contained host tool for a board with a UF2 mass-storage
bootloader. It first checks whether the target UF2 volume is already mounted;
when it is, it copies the converted image directly. Otherwise it performs a
USB CDC 1200-bps touch, waits for the volume label and copies the result. It
has no Python or shell dependency at upload time:

```
uf2upload --input firmware.bin --port COM7 --volume XIAOC5BOOT \
  --address 0x08008000 --family 0x00C5C5C5 --max-size 1015808
```

Use `--skip-touch` to disable the CDC touch when no bootloader volume is
currently mounted. The source is built for the host package with
`make -C src/uf2upload`.

Linux ARM64/AArch64 builds are provided under `linux/aarch64/uf2upload`.
From an x86_64 Linux host, they can be rebuilt with:

```
make -C src/uf2upload aarch64
```

The ARM64 build is cross-compiled; see
[`src/linux-aarch64/LOCAL_VALIDATION.md`](src/linux-aarch64/LOCAL_VALIDATION.md)
for QEMU-based validation and its limitations.
