/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef IFS_UFS1_MUTATION_H
#define IFS_UFS1_MUTATION_H
#include "ufs_native.h"
typedef struct Ufs1Mutation Ufs1Mutation;
typedef struct Ufs1RelocationPlan Ufs1RelocationPlan;
/* Writable access is qualified only for the clean native one-group profile.
 * The host grants the exclusive durable lease and retains it until close. */
int ufs1_mutation_open(const IfsFsHostRuntimeV2 *, const LdUfsSummary *, Ufs1Mutation **);
int ufs1_mutation_create(Ufs1Mutation *, const char *, uint32_t);
int ufs1_mutation_write(Ufs1Mutation *, const char *, uint64_t, const void *, uint32_t);
int ufs1_mutation_faulted(const Ufs1Mutation *);
void ufs1_mutation_counts(const Ufs1Mutation *, uint64_t *, uint64_t *);
void ufs1_mutation_close(Ufs1Mutation *);
int ufs1_relocation_plan(Ufs1Mutation *,const char *,uint32_t,Ufs1RelocationPlan **);
void ufs1_relocation_release(Ufs1Mutation *,Ufs1RelocationPlan *);
int ufs1_relocation_marker(const IfsFsHostRuntimeV2 *);
int ufs1_relocation_recover(const IfsFsHostRuntimeV2 *,int,uint64_t *,IfsFsVolumeInfoV2 *);
int ufs1_relocation_execute(Ufs1Mutation *,Ufs1RelocationPlan *,uint64_t *);
int ufs1_relocation_verify(Ufs1Mutation *,Ufs1RelocationPlan *);
#endif
