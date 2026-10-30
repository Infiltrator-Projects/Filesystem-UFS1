# Filesystem-UFS1 — UFS1.so

Independent **UFS1** on-disk filesystem driver for InfiltratorOS.
This module rejects UFS2 media and installs only `/System/Filesystems/UFS1.so`.

This is a C port of the validated UFS1 execution path from the original
[Filesystem-UFS](https://github.com/Infiltrator-Projects/Filesystem-UFS2)
repository (snapshot `a64350b9f7bd13456689415f7c52171439d72758`).
Its C engine supports UFS1 little-endian and big-endian identification,
analysis, safe staged Defrag, Growth Defrag and Recover via the existing
versioned Defragmenter host ABI. UFS2's Test Media creator and UFS2-specific
raw verifier deliberately do not belong to this module.

Build: `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ctest --test-dir build --output-on-failure`.

**Qualification limitation:** this split needs independent real UFS1 media,
allocation and mutation/recovery validation before a finished-driver claim.
Module interface version V1 is independent of the UFS1 disk format generation.
