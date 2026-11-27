# UFS1: technical reference

## Origins and scope

UFS1 descends from the Berkeley Fast File System introduced in 4.2BSD. It improved Unix allocation locality through cylinder groups and small fragments. Later 4.4BSD inode and directory revisions, Sun UFS and other vendor derivatives are related but not identical. This reference uses the modern BSD-compatible UFS1 profile, notes historical differences, and does not claim that every UFS-labelled disk is safely writable. Magic 0x00011954 identifies the ordinary format.

Marshall Kirk McKusick and colleagues described the FFS allocation rationale in their 1984 paper A Fast File System for UNIX. UFS1 remains a distinct classic inode/cylinder-group format; BSD soft updates and later journals are implementation and feature profiles, not universal UFS1 properties.

## Geometry and address units

The Berkeley Fast File System divides a volume into cylinder groups. A filesystem block B contains F=B/f fragments of size f. F is normally 1, 2, 4 or 8. Stored block addresses refer to fragments, not necessarily whole filesystem blocks or disk sectors. Physical byte offset equals partition start plus fragment number times f. Validate B and f as powers of two, their ratio, all group bounds, and all products before trusting metadata. Cylinder geometry is historical placement information, not the geometry of a modern SSD.

## Superblock discovery and fields

Read candidate superblocks of 8192 bytes at the profile-appropriate offsets, typically 8192 for UFS1 or 65536 for UFS2; alternative locations 0 and 262144 require profile checks. Detect byte order from the magic at byte 1372. Common 32-bit fields, offsets from superblock: sblkno 8, cblkno 12, iblkno 16, dblkno 20, old cgoffset 24, old cgmask 28, ncg 44, bsize 48, fsize 52, frag 56, minfree 60, bshift 80, fshift 84, fragshift 96, fsbtodb 100, sbsize 104, nindir 116, inopb 120, cssize 156, cgsize 160, ipg 184, fpg 188. Do not interpret saved in-memory pointer fields as disk addresses.

## Cylinder group placement

For group g, cgbase=g*fpg. UFS1 cgstart=cgbase+cgoffset*(g & complement(cgmask)); UFS2 cgstart=cgbase. The backup superblock, group header, inode table and initial data area occur at cgstart+sblkno, +cblkno, +iblkno and +dblkno respectively. These are fragment addresses. Check group index and last-group size. UFS1 uses rotational staggering to distribute metadata; the UFS2 geometry simplifies placement. The group header and allocation maps may not occupy identical offsets across historical variants.

## Cylinder group header

In the modern BSD cylinder group layout, 32-bit fields include magic at 4 (0x00090255), group number 12, data fragment count 20, directory count 24, free whole blocks 28, free inodes 32, free fragments 36, block/fragment/inode rotors 40/44/48. Fragment summary begins at 52. Map offsets are stored at 92 (inode used), 96 (fragment free), 100 (next free offset), 104 (cluster summary), 108 (cluster bitmap). Validate the entire map extent against cgsize and actual group capacity. Treat older cylinder group layouts as separate profiles.

## Bitmap accounting

The fragment map uses set bits for free space; the inode map uses set bits for allocated inodes. Within each byte the bit index is least significant first in the BSD bitmap representation. A whole free block consists of F aligned free fragments; it must not also be counted as F free partial fragments in summary statistics. The free-fragment run histogram and optional contiguous-cluster summary accelerate allocation. Recompute counters from the maps; reserve superblocks, summary areas, group metadata, inode tables and any other allocated metadata. Never use the free count alone to authorize a write.

## Inode lookup

For inode n, g=floor(n/ipg), local=n mod ipg; inode block index=floor(local/inopb), slot=local mod inopb. The inode lies at (cgstart+iblkno+inode_block_index*F)*f+slot*inode_size relative to the partition. Inode 2 is the root. Inode 0 is not a regular directory target. Check group allocation, inode-table bounds, and inode type. A stale directory record can identify a reused inode, so directory and allocation consistency are independent checks.

## UFS1 dinode byte layout

The 128-byte BSD inode has mode at 0 (16 bits), link count 2 (16), legacy owner IDs or profile-specific field 4 (4), size 8 (64), atime seconds/nanoseconds 16/20, mtime 24/28, ctime 32/36. Twelve 32-bit direct fragment pointers begin at 40 and three indirect at 88. Flags 100, allocated sectors 104, generation 108, uid 112, gid 116, modern modrev 120 (64); older profiles use the tail differently. Inline symlinks occupy the pointer union when the profile permits. Legacy inode format and ownership fields must be validated before interpreting modern offsets.

## Direct and indirect data

Twelve direct addresses precede single, double and triple indirect pointers. With N=B/pointer_size, logical blocks 0..11 use direct pointers, the next N use single indirection, the next N squared double, the next N cubed triple. Subtract the preceding ranges and select indices by quotient and remainder. Each pointer represents a fragment address. Indirect blocks are full blocks and require full aligned allocation. Zero pointers represent holes; do not read physical sector zero as file data. Limit reads to the inode's logical size, and reject overflowing or cyclic indirect paths.

## Fragments and sparse tails

With B=8192 and f=1024, a 2500-byte file uses three fragments in its first direct block, not eight. A 10500-byte file uses one full 8192-byte block and three fragments for its 2308-byte direct tail. Under the BSD blksize rule, blocks addressed indirectly use full block allocation, even when the final logical data is shorter. As a direct tail grows, the allocator may extend its fragment run or move the tail to a larger free run. Preserve the file's data, zero newly visible bytes, and publish allocation and pointer changes in the appropriate consistency order.

## Worked UFS1 inode and indirection

Example B=8192, f=1024, ipg=2048, fpg=32768, iblkno=32, cgoffset=8 and a mask that staggers group 1 by 8. Inode 2050 is group 1, local slot 2, inode table at fragment 32808. Its byte offset is 33595648. With 4-byte pointers N=2048; logical block 2060 is the first doubly indirect data block. At that point both index positions are zero. The inode size is 128 and inopb=64. Check the stored superblock parameters rather than using these example constants.

## Directory records and names

A directory is a file of variable-size records constrained to 512-byte directory blocks. Modern record fields: inode 0 (32 bits), record length 4 (16 bits), type 6 (8 bits), name length 7 (8 bits), name at 8. Legacy formats use a 16-bit name length at offset 6; the byte order and inode format determine interpretation. Minimum record length is align4(8+namelen+1). Validate nonzero aligned lengths, boundary containment, terminator and inode range. Inode zero marks an unused record. Insertion splits excess record space; deletion can merge space within the directory block. Verify dot and dot-dot and hard-link counts separately.

## Allocation and namespace changes

A new inode requires a free inode bit, initialized metadata, then a valid directory reference. Allocation seeks locality by group, chooses aligned free whole blocks or an appropriate fragment run, updates the maps and summary, and initializes data before publishing pointers. On unlink, remove the name and decrement links; reclaim only when the last link and open-file lifetime permit. Renaming directories requires cycle prevention, parent-link correction and ordered directory updates. Account for indirect blocks and extended attributes as well as user data. Reserve policy (minfree) is separate from physical free space.

## Consistency and qualification

Classical FFS does not have an unconditional on-disk redo journal. Soft updates impose metadata dependencies; soft-updates journaling adds a particular recovery protocol. Other BSD/Solaris journal schemes are not interchangeable. A checker must reconcile inode allocation, block ownership, fragment boundaries, link counts, directory reachability, group summaries and superblock totals. Do not mistake a clean flag for proof of consistency. An independent writer needs a validated profile for the enabled features, including snapshots, checksums and journal behavior. Test on disposable images from native newfs and verify with native fsck; include interrupted allocations and renames, not only clean read-back.

## Implementation and qualification boundary

Historical revision 184d2e4bb9c3 exposed probe, mount, stat, read and format, including native-endian interpretation. An inventory must preserve host I/O errors and avoid caching partial ownership; inject faults before lazy inventory construction. Retained relocation internals do not establish a qualified public mutation contract.

Common V2 is the independent provider interface: https://github.com/Infiltrator-Projects/Libraries/blob/main/docs/FILESYSTEM_COMMON_ABI_V2.md . Negotiate real operation masks and media profiles. Use bounded host I/O, exclusive unmounted ownership and durable flush for mutation; distinguish unsupported, corrupt, I/O and stale-handle results. Test Media and Defragmenter use the same engine only for supported operations. Hosted, freestanding, BOOT, kernel, recovery and package qualification are independent. Current capability and release status belongs to the repository README and exact-source qualification records; historical evidence is not a current status claim.

Historical source reference: https://github.com/Infiltrator-Projects/Filesystem-UFS1/tree/184d2e4bb9c3 .

## Sources and independent implementation

Primary design: McKusick, Joy, Leffler and Fabry, A Fast File System for UNIX (1984). Layout reference: FreeBSD release/14.2.0, sys/ufs/ffs/fs.h, sys/ufs/ufs/dinode.h and sys/ufs/ufs/dir.h: https://github.com/freebsd/freebsd-src/tree/release/14.2.0/sys/ufs . Independent cross-check: Linux v6.12 fs/ufs/ufs_fs.h and fs/ufs/balloc.c: https://github.com/torvalds/linux/tree/v6.12/fs/ufs . The original  Project provider claims in that appendix are historical, not current qualification. Exact journal replay and all vendor variants require additional source and fixture verification.
