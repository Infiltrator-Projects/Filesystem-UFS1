# UFS1 Common V2 migration status

The native `native/ufs_native.c` implementation supplies all Common V2
on-media geometry and allocation validation, checked native BSD inode and
directory traversal, and actual file reads. It uses an authenticated,
partition-relative Common V2 host for every production read. Real disposable
UFS1 images test root/file stat, multi-entry directory enumeration,
contents from inode extents, missing paths, invalid traversal, corrupted
bitmaps and read-only nonmutation.

The production UFS1.so exports only Common V2, without Linux VFS,
historical worker or V1 Defragmenter service imports. The independent native
writer and Linux kernel adapter remain in repository source only. The old
.ko release path is disabled. Portable DEB and source-embedded RUN carry
exactly UFS1.so plus its PDF. **Concurrent read-only mounts now use independent session slots and
non-recycled opaque tokens, so unmounting one volume cannot invalidate its
peers.** Disposable Common V2 regression tests cover concurrent readers,
stale handles and byte-for-byte media nonmutation.

**Not yet BOOT qualified:** same engine needs a freestanding EFI-compatible
build, embedded ELF, no libc dependence in firmware, actual unmodified BOOT
validator acceptance and OVMF real kernel/initramfs read/nonmutation tests.
No new official release is permitted until those checks pass.
