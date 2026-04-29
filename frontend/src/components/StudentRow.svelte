<script lang="ts">
  import type { Mastery } from '../types/models'
  import type { UserType, SubjectType, StatusType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'

  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import Link from './Link.svelte'
  import StatusEdit from './StatusEdit.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import Statuses from './Statuses.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
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

  const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)
  const today = new Date()
  let statusWip = $state<Partial<StatusType> | null>(null)
  let isStatusEditorOpen = $state<boolean>(false)
  let statusesKey = $state<number>(0) // key used to force re-render of Statuses component

  const handleEditStatus = async (status: Partial<StatusType> | null) => {
    if (status?.id) {
      statusWip = {
        ...status,
      }
    } else {
      statusWip = {
        subjectId: null,
        studentId: student.id,
        schoolId: $dataStore.currentSchool.id,
        beginAt: sixtyDaysAgo.toISOString().split('T')[0],
        endAt: today.toISOString().split('T')[0],
      }
    }
    isStatusEditorOpen = true
  }

  const handleStatusDone = async () => {
    isStatusEditorOpen = false
    statusesKey++
  }
</script>

<span>
  <span class="item student-name">
    <Link to={`/students/${student.id}`}>{student.name}</Link>
  </span>

  {#if $hasUserAccessToFeature('status', 'create', { studentGroupIds: student.groupIds })}
    <ButtonIcon
      options={{
        iconName: 'achievement',
        classes: 'bordered ms-1',
        title: 'Legg til ny status',
        onClick: () => handleEditStatus(null),
      }}
    />
  {/if}

  {#key statusesKey}
    <Statuses {student} subject={null} />
  {/key}
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

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit
      status={statusWip}
      {student}
      subject={null}
      goals={null}
      onDone={handleStatusDone}
    />
  {/if}
</Offcanvas>

<style>
</style>
