/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef IFS_UFS1_MUTATION_H
#define IFS_UFS1_MUTATION_H
#include "ufs_native.h"
typedef struct Ufs1Mutation Ufs1Mutation;
/* Writable access is qualified only for the clean native one-group profile.
 * The host grants the exclusive durable lease and retains it until close. */
int ufs1_mutation_open(const IfsFsHostRuntimeV2 *, const LdUfsSummary *, Ufs1Mutation **);
int ufs1_mutation_create(Ufs1Mutation *, const char *, uint32_t);
int ufs1_mutation_write(Ufs1Mutation *, const char *, uint64_t, const void *, uint32_t);
int ufs1_mutation_faulted(const Ufs1Mutation *);
void ufs1_mutation_counts(const Ufs1Mutation *, uint64_t *, uint64_t *);
void ufs1_mutation_close(Ufs1Mutation *);
#endif
