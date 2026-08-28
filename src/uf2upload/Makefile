CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Werror
AARCH64_CXX ?= aarch64-linux-gnu-g++
AARCH64_STRIP ?= aarch64-linux-gnu-strip
AARCH64_DEST = ../../linux/aarch64/uf2upload

ifeq ($(OS),Windows_NT)
  DEST = ../../win/uf2upload.exe
  LDFLAGS ?= -static -static-libgcc -static-libstdc++
else
  LDFLAGS ?=
  UNAME_S := $(shell uname -s)
  ifeq ($(UNAME_S),Darwin)
    DEST = ../../macosx/uf2upload
  else
    DEST = ../../linux/x86_64/uf2upload
  endif
endif

.PHONY: all aarch64 clean

all: $(DEST)

$(DEST): uf2upload.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

aarch64: $(AARCH64_DEST)

$(AARCH64_DEST): uf2upload.cpp
	$(AARCH64_CXX) $(CXXFLAGS) -o $@ $<
	$(AARCH64_STRIP) $@

clean:
	rm -f ../../win/uf2upload.exe ../../macosx/uf2upload ../../linux/x86_64/uf2upload $(AARCH64_DEST)
