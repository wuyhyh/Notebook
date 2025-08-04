#include <efi.h>
#include <efilib.h>

EFI_STATUS efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable)
{
	InitializeLib(ImageHandle, SystemTable);

	int count = 0;
	while (1) {
		Print(L"[UEFI] Hello! Count = %d\n", count++);
		// 延时 1 秒（单位为微秒）
		udelay(1000000);
	}

	return EFI_SUCCESS;
}
