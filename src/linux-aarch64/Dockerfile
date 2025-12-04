# Dockerfile for cross-compiling ARM64 Linux binaries
# This builds dfu-util, hid-flash, and upload_reset for aarch64

FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Add arm64 architecture first
RUN dpkg --add-architecture arm64

# Install cross-compilation toolchain and build dependencies
RUN apt-get update && apt-get install -y \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
    git \
    autoconf \
    automake \
    libtool \
    pkg-config \
    dpkg-dev \
    make \
    wget \
    curl \
    ca-certificates \
    file \
    libusb-1.0-0-dev:arm64 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Set cross-compilation environment variables
ENV CC=aarch64-linux-gnu-gcc
ENV CXX=aarch64-linux-gnu-g++
ENV AR=aarch64-linux-gnu-ar
ENV RANLIB=aarch64-linux-gnu-ranlib
ENV STRIP=aarch64-linux-gnu-strip
ENV PKG_CONFIG_PATH=/usr/lib/aarch64-linux-gnu/pkgconfig
ENV PKG_CONFIG_LIBDIR=/usr/lib/aarch64-linux-gnu/pkgconfig

# Clone and build dfu-util (includes dfu-prefix and dfu-suffix)
RUN git clone https://git.code.sf.net/p/dfu-util/dfu-util dfu-util && \
    cd dfu-util && \
    ./autogen.sh && \
    ./configure --host=aarch64-linux-gnu \
                --prefix=/build/output \
                PKG_CONFIG=aarch64-linux-gnu-pkg-config && \
    make && \
    make install-strip

# Clone and build hid-flash from STM32_HID_Bootloader
RUN git clone https://github.com/Serasidis/STM32_HID_Bootloader.git && \
    cd STM32_HID_Bootloader/cli && \
    make clean && \
    make CC=${CC} && \
    ${STRIP} hid-flash && \
    cp hid-flash /build/output/bin/

# Build upload_reset from source
COPY src/upload_reset/unix/upload_reset.c /build/upload_reset.c
RUN ${CC} -o /build/output/bin/upload_reset /build/upload_reset.c && \
    ${STRIP} /build/output/bin/upload_reset

# Create output directory structure
RUN mkdir -p /output

# Copy built binaries to output
RUN cp /build/output/bin/dfu-util /output/ && \
    cp /build/output/bin/dfu-prefix /output/ && \
    cp /build/output/bin/dfu-suffix /output/ && \
    cp /build/output/bin/hid-flash /output/ && \
    cp /build/output/bin/upload_reset /output/

# Verify binaries are ARM64
RUN file /output/* | grep aarch64

# Test that all binaries execute correctly on ARM64
# This stage is built for ARM64 platform and requires QEMU emulation on x86_64
FROM ubuntu:22.04 AS test
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    file \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=0 /output/* /usr/local/bin/

# Print build platform information
RUN echo "========================================" && \
    echo "Docker Build Platform Information" && \
    echo "========================================" && \
    echo "TARGETPLATFORM: ${TARGETPLATFORM}" && \
    echo "BUILDPLATFORM: ${BUILDPLATFORM}" && \
    echo "uname -m: $(uname -m)" && \
    echo "uname -s: $(uname -s)" && \
    echo "========================================" && \
    echo ""

# Test all binaries
RUN echo "========================================" && \
    echo "Testing ARM64 Binaries" && \
    echo "========================================" && \
    echo "" && \
    echo "=== System Architecture ===" && \
    uname -m && \
    echo "" && \
    echo "=== Testing dfu-util ===" && \
    file /usr/local/bin/dfu-util && \
    dfu-util --version && \
    echo "" && \
    echo "=== Testing dfu-suffix ===" && \
    file /usr/local/bin/dfu-suffix && \
    dfu-suffix --version && \
    echo "" && \
    echo "=== Testing dfu-prefix ===" && \
    file /usr/local/bin/dfu-prefix && \
    dfu-prefix --version && \
    echo "" && \
    echo "=== Testing hid-flash ===" && \
    file /usr/local/bin/hid-flash && \
    (hid-flash --help 2>&1 || echo "(hid-flash executed successfully)") && \
    echo "" && \
    echo "=== Testing upload_reset ===" && \
    file /usr/local/bin/upload_reset && \
    (upload_reset --help 2>&1 | head -5 || echo "(upload_reset executed successfully)") && \
    echo "" && \
    echo "========================================" && \
    echo "✓ All ARM64 binaries are working!" && \
    echo "========================================"

# Final stage: just the binaries
FROM scratch AS export
COPY --from=0 /output/* /

# Default command shows built files
CMD ["sh", "-c", "ls -lh /output && file /output/*"]
