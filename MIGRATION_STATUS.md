# UFS1 Common V2 and BOOT qualification

The source-owned native UFS1 filesystem engine supplies read-only Common V2
PROBE/MOUNT/UNMOUNT, STAT/LIST/READ and DEFRAG.MAP using authenticated
partition-relative bounded host I/O, genuine BSD inode/dirent records,
the UFS1 allocation map and indirect file block traversal. Independent
mounted volumes use non-recycled opaque tokens and distinct inventories.

The hosted and freestanding profiles compile the same native/ufs_native.c
and module/ufs_module.c. The installed UFS1.so includes a no-import
freestanding ELF embedded in .infiltrator_boot; production exports Common
V2 only. Historical V1, Linux kernel and worker sources remain in the
repository but are not shipped as runtime substitutes.

The unmodified production BOOT 0.1.77 validator qualifies both standalone
firmware and installed SO. Disposable OVMF reads an EFI-stub kernel and
initramfs from a real UFS1 test volume via the Common V2 module staged in
EFI/BOOT/drivers_x64, refuses corrupt-superblock media and verifies no
source-volume mutation. Portable Debian and CPU-native source RUN module
binaries must also pass the same validator. Immutable release publication
is gated on exact-commit hosted and OVMF success.

Physical Secure Boot signature/MOK integration remains a separate
environment-specific qualification; CI does not alter live NVRAM or ESP.
