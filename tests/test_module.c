/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "ifs_ufs_module_v1.h"
#include "ifs_ufs_probe_v1.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(void) {
    const IfsUfsModuleV1 *m = infiltrator_filesystem_ufs_v1();
    const IfsUfsProbeV1 *p = infiltrator_filesystem_ufs_probe_v1();
    if (!m || m->abi_version != IFS_UFS_MODULE_V1 ||
        m->structure_bytes < sizeof(*m) || !m->format_id ||
        strcmp(m->format_id, "ufs1") || m->capabilities != IFS_UFS_CAP_RUN ||
        !m->run || m->format_test_media || !p ||
        p->abi_version != IFS_UFS_PROBE_ABI_V1 ||
        p->structure_bytes < sizeof(*p) || !p->format_id ||
        strcmp(p->format_id, "ufs1") || !p->accepts_volume ||
        p->accepts_volume("/nonexistent-ufs1-test-volume") == 0) return 1;
    char image[] = "/tmp/ufs1-only-test-XXXXXX";
    int fd = mkstemp(image);
    if (fd < 0) return 2;
    const unsigned char one[4] = {0x54, 0x19, 0x01, 0x00};
    const unsigned char two[4] = {0x19, 0x01, 0x54, 0x19};
    const off_t magic = 8192 + 1372;
    int good = ftruncate(fd, 65536) == 0 &&
        pwrite(fd, one, sizeof(one), magic) == (ssize_t)sizeof(one) &&
        p->accepts_volume(image) == 0 &&
        pwrite(fd, two, sizeof(two), magic) == (ssize_t)sizeof(two) &&
        p->accepts_volume(image) != 0;
    close(fd);
    unlink(image);
    return good ? 0 : 3;
}
