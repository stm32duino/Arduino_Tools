CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Werror

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

.PHONY: all clean

all: $(DEST)

$(DEST): uf2upload.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

clean:
	rm -f ../../win/uf2upload.exe ../../macosx/uf2upload ../../linux/x86_64/uf2upload
