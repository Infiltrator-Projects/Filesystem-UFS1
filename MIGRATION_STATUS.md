# UFS1 split status

Source: canonical predecessor Filesystem-UFS2 at a64350b9f7bd13456689415f7c52171439d72758.

- Dedicated UFS1.so, independently installed and built with IFS_UFS_MAJOR=1.
- Module reports format_id=ufs1; a read-only probe rejects UFS2 magic.
- Production parser rejects both UFS2 byte orders.
- Existing UFS1 analysis/relocation/recovery logic retained.
- UFS2-only formatter and raw UFS2 verifier deliberately excluded.
- Independent real-media, recovery and power-failure qualification pending.

## Common V2 allocation verification (1.0.9)
Read-only CORE mount and VOLUME query verify each cylinder-group allocation
bitmap through partition-relative host I/O before reporting superblock free
space. Totals that disagree, damaged group headers or inconsistent bitmap
geometry fail closed. The native UFS1 scanner remains solely in this repo.
These totals do not replace file/directory traversal, full fsck, the native
DEFRAG extent map, transaction recovery or real-media power-failure testing.

## Common V2 native file extent mapping (1.0.10)
The independent UFS1 module now exposes read-only DEFRAG.MAP using its
existing validated native cylinder-group, inode and indirect-block scanner
through authenticated partition-relative Common V2 host I/O. The provider
resolves absolute directory paths itself and returns actual paginated file
extents. Sparse logical offsets are preserved as gaps. No retired V1 service
binding is required for the V2 mapper. The pre-existing native transaction
writer and recovery remain unchanged and are not advertised as V2 PLAN,
EXECUTE, VERIFY or RECOVER. Synthetic API tests are not equivalent to
real-world UFS1 fixture or physical-media qualification.

## Common V2 native BSD dirent exact-length coverage (1.0.11)
The filesystem-owned directory scanner now accepts a valid record whose
byte length equals the eight-byte header plus the filename byte count.
A native C synthetic-on-disk inode/dirent test covers a four-byte name in
an exact 12-byte dirent while retaining the earlier multi-record, missing
file, and corrupted free-bitmap-owned data pointer checks. Source-owned
DEFRAG.MAP remains read-only; V2 writer/recovery remains unqualified.
