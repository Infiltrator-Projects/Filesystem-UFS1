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

## Installer files

- `/System/Filesystems/UFS1.so`
- `/System/Resources/Documentation/Filesystem-UFS1.pdf`
- `/System/Kernel/Filesystems/ufs1.ko`

The published Debian package installs these three regular files. A manual native RUN compiles the shared object and Linux adapter locally, generates the PDF, and replaces all three files. It uses the running kernel headers by default. Use `--kernel-build DIRECTORY` for a prepared kernel build with `Module.symvers`. The kernel module is stored for manual use.

InfiltratorOS calls `--system-package-mode` and decides which outputs need updating. Its worker builds a missing or older SO, repairs the PDF independently, and stores the matching released kernel module when available. Use `--build-only --output DIRECTORY` to build a Debian package.
