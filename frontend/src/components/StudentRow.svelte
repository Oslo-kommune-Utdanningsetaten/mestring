<script lang="ts">
  import type { Mastery } from '../types/models'
  import type { UserType, SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import Link from './Link.svelte'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'

  type MasteryState = {
    mastery?: Mastery
    missingReason?: typeof MISSING_REASON_NO_OBSERVATIONS | typeof MISSING_REASON_NO_GOALS
  }

  let {
    student,
    subjects,
    masteryBySubjectId,
  }: {
    student: UserType
    subjects: SubjectType[]
    masteryBySubjectId?: Record<string, MasteryState>
  } = $props()
</script>

<span class="item student-name">
  <Link to={`/students/${student.id}`}>{student.name}</Link>
</span>
{#each subjects as subject}
  <span class="item">
    {#if masteryBySubjectId?.[subject.id]?.mastery}
      <MasteryLevelBadge
        masteryData={masteryBySubjectId[subject.id].mastery!}
        masterySchema={$dataStore.defaultMasterySchema}
      />
    {:else if masteryBySubjectId?.[subject.id]?.missingReason === MISSING_REASON_NO_OBSERVATIONS}
      <MasteryLevelBadge isBadgeEmpty={true} />
    {:else if masteryBySubjectId?.[subject.id]?.missingReason === MISSING_REASON_NO_GOALS}
      <MasteryLevelBadge isBadgeVoid={true} />
    {/if}
  </span>
{/each}

<style>
</style>
