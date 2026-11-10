/* SPDX-License-Identifier: GPL-3.0-or-later
 * UFS1 provider: sole exported contract is Common V2 CORE.
 */
#include <infiltratr/filesystem_module_v2.h>
#include "ufs_native.h"
static int probe(const IfsFsHostRuntimeV2 *host,uint32_t *variant)
{
    LdUfsSummary summary;
    int result;
    if(!variant)return IFS_FS_INVALID;
    *variant=0u;
    result=ufs_read_summary_host_v2(host,&summary);
    if(result!=IFS_FS_OK)return result;
    if(summary.variant!=LD_UFS_VARIANT_UFS1_LE &&
       summary.variant!=LD_UFS_VARIANT_UFS1_BE)
        return IFS_FS_NOT_FOUND;
    *variant=(uint32_t)summary.variant;
    return IFS_FS_OK;
}
static const IfsFsCoreOpsV2 core={
    .header={IFS_FS_GROUP_ABI_V2,sizeof(IfsFsCoreOpsV2),
             IFS_FS_GROUP_CORE,0u,IFS_FS_CORE_PROBE},
    .probe=probe
};
static const IfsFsGroupHeaderV2 *query(
    uint32_t group_id,uint32_t minimum,uint32_t maximum)
{
    return group_id==IFS_FS_GROUP_CORE &&
           minimum<=IFS_FS_GROUP_ABI_V2 &&
           maximum>=IFS_FS_GROUP_ABI_V2 ? &core.header : NULL;
}
static const IfsFsModuleApiV2 api={
    .abi_version=IFS_FS_COMMON_ABI_V2,
    .structure_bytes=sizeof(IfsFsModuleApiV2),
    .format_id="ufs1",
    .runtime_profiles=IFS_FS_PROFILE_HOSTED,
    .group_mask=IFS_FS_GROUP_BIT(IFS_FS_GROUP_CORE),
    .query_group=query
};
__attribute__((visibility("default")))
const IfsFsModuleApiV2 *infiltrator_filesystem_api_v2(void)
{
    return &api;
}
