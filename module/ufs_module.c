/* SPDX-License-Identifier: GPL-3.0-or-later
 * UFS1 identity and read-only dispatch guard. UFS2 media is never accepted.
 */
#include "ifs_ufs_module_v1.h"
#include "ifs_ufs_probe_v1.h"
#include "ufs_native.h"
int ifs_ufs_worker_main(int argc, char **argv);
int ifs_bind_services(const IfsDefragServicesV1 *);
void ifs_unbind_services(void);
static int run(int argc, char **argv, const IfsDefragServicesV1 *services) {
    if (ifs_bind_services(services) != 0) return 1;
    const int result = ifs_ufs_worker_main(argc, argv);
    ifs_unbind_services();
    return result;
}
static const IfsUfsModuleV1 api = {
    IFS_UFS_MODULE_V1, sizeof(IfsUfsModuleV1), "ufs1",
    IFS_UFS_CAP_RUN, run, NULL
};
const IfsUfsModuleV1 *infiltrator_filesystem_ufs_v1(void) { return &api; }
static int accepts_volume(const char *path) {
    return path && ufs_probe(path) ? 0 : -1;
}
static const IfsUfsProbeV1 probe = {
    IFS_UFS_PROBE_ABI_V1, sizeof(IfsUfsProbeV1), "ufs1", accepts_volume
};
const IfsUfsProbeV1 *infiltrator_filesystem_ufs_probe_v1(void) { return &probe; }
