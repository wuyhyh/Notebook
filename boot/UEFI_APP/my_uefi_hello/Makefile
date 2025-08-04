# Makefile

TARGET = BOOTX64.EFI
SRC = hello.c
OBJ = hello.o

ARCH = x86_64
EFIINC = /usr/include/efi
EFILIB = /usr/lib64/gnu-efi
EFILDS = elf_x86_64_efi.lds

CFLAGS = -I$(EFIINC) -I$(EFIINC)/$(ARCH) -fPIC -fshort-wchar -mno-red-zone -m64 -DEFI_FUNCTION_WRAPPER
LDFLAGS = -nostdlib -znocombreloc -T $(EFILDS) -shared -Bsymbolic -L/usr/lib/libelf.a /usr/lib/libgnuefi.a

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ)
	ld $(LDFLAGS) $^ -o $@

%.o: %.c
	gcc $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o *.efi *.EFI

