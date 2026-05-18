<script lang="ts">
  import type { Mastery } from '../types/models'
  import type { UserType, SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'

  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import UserNameLink from './UserNameLink.svelte'
  import Statuses from './Statuses.svelte'

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

  let statusesKey = $state<number>(0) // key used to force re-render of Statuses component
</script>

<span class="item student-name">
  <UserNameLink user={student} />
  <span class="student-actions">
    {#key statusesKey}
      <Statuses {student} subject={null} />
    {/key}
  </span>
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
    {:else}
      <div class="d-flex align-items-center gap-2 text-secondary small py-2">
        <span
          class="spinner-border spinner-border-sm"
          role="status"
          aria-label="Henter data"
        ></span>
      </div>
    {/if}
  </span>
{/each}

<style>
  .student-actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
</style>
