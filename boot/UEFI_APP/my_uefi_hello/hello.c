// hello.c
#include <efi.h>
#include <efilib.h>

EFI_STATUS
efi_main (EFI_HANDLE image_handle, EFI_SYSTEM_TABLE *system_table)
{
	InitializeLib(image_handle, system_table);
	Print(L"Hello from my own UEFI bootloader!\n");
	return EFI_SUCCESS;
}
