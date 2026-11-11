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
