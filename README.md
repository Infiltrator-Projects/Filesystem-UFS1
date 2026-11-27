# Filesystem-UFS1

## 1. Purpose and format scope

Unix File System UFS1, distinct from UFS2. This repository owns the format-specific implementation of `UFS1.so` for InfiltratorOS.

## 2. On-disk architecture and invariants

Cylinder groups, inode tables, allocation bitmaps, direct and indirect references and native byte order govern ownership. Preserve UFS1 little- and big-endian interpretations; reject UFS2 media. Inventory construction must preserve host I/O failures rather than publish partial allocation state.

## 3. Common V2 implementation and capabilities

The current descriptor declares probe, mount, stat, read and format, superseding the old probe-only description. The historical analysis and relocation internals do not establish a Common V2 mutation contract. The canonical entry point is `infiltrator_filesystem_api_v2`. Consumers must negotiate the actual profile and operation masks and use bounded, partition-relative host I/O. A source-level callback does not by itself establish that every format variant or host profile is qualified.

## 4. Integrity, mutation, allocation and recovery

Lazy inventory fault injection must occur before caching so the error path is actually exercised. Native allocation, mutation and recovery require specific qualification; UFS2 fixtures are not UFS1 evidence. For destructive operations, require the applicable exclusive writable host, durability contract and format-specific validation. Never silently substitute a kernel or FUSE driver or treat a rejected or unavailable operation as success. Preserve original disk-format semantics; relocation and recovery are separate from ordinary file I/O.

## 5. Build, installation and release

The target installation is `/System/Filesystems/UFS1.so` and `/System/Resources/Documentation/Filesystem-UFS1.pdf`. The project release policy is a portable amd64 DEB and a CPU-native source-first RUN, with GitHub's automatic source archive; do not treat this policy statement as verification of the current installer payload. The release workflow is the authoritative executable build and package specification. Historical adapters and test artifacts are not additional production filesystem authorities.

## 6. Qualification and limitations

[Recorded qualification workflow](https://github.com/Infiltrator-Projects/Filesystem-UFS1/actions/runs/45526886448) · [Current workflows](https://github.com/Infiltrator-Projects/Filesystem-UFS1/actions?query=branch%3Amain). A successful workflow establishes the tested scope only, not complete original-format parity, physical-media crash safety, or production BOOT/kernel integration. Use disposable images for destructive qualification.

## 7. Technical references and provenance

- [Provider implementation](module/ufs_module.c)
- [Native design or source provenance](native/filesystems/ufs/DESIGN.md)
- [Migration and source history](MIGRATION_STATUS.md)
- [Original-format reference source](docs/UFS1.pdfstreams) and [PDF](docs/UFS1.pdf)
- [Project philosophy](docs/PHILOSOPHY.md)
- [Common ABI](https://github.com/Infiltrator-Projects/Libraries)

The original-format reference and historical migration notes describe different evidence from the current production provider. When descriptions disagree, the current exported descriptor, implementation, executable tests and exact-revision release evidence take precedence.

The [engineering reference](docs/UFS1-TECHNICAL-REFERENCE.md) adds field-level original-format guidance. The PDF and editable reference contain one integrated manual.
