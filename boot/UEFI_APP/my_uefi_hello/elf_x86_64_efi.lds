OUTPUT_FORMAT("elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_start)
SECTIONS
{
  . = 0;
  .text : {
    *(.text)
  }
  .sdata : {
    *(.sdata)
  }
  .data : {
    *(.data)
  }
  .dynamic : {
    *(.dynamic)
  }
  .rodata : {
    *(.rodata*)
  }
  .got : {
    *(.got)
  }
  .efi : {
    KEEP (*(.efi))
  }
  .rel : {
    *(.rel)
  }
  .rela : {
    *(.rela)
  }
  .rel.plt : {
    *(.rel.plt)
  }
  .rela.plt : {
    *(.rela.plt)
  }
  .rel.dyn : {
    *(.rel.dyn)
  }
  .rela.dyn : {
    *(.rela.dyn)
  }
  .plt : {
    *(.plt)
  }
  .bss : {
    *(.bss)
    *(COMMON)
  }
  /DISCARD/ : {
    *(.note.GNU-stack)
  }
}

