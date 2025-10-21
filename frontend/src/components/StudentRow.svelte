<script lang="ts">
  import type { Mastery, GoalDecorated } from '../types/models'
  import type { UserType, SubjectType, GroupType } from '../generated/types.gen'
  import { goalsList } from '../generated/sdk.gen'
  import { goalsWithCalculatedMasteryBySubjectId, aggregateMasterys } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'

  let { student, subjects, groups } = $props<{
    student: UserType
    subjects: SubjectType[]
    groups: GroupType[]
  }>()

  type MasteryState = {
    mastery?: Mastery
    missingReason?: typeof MISSING_REASON_NO_OBSERVATIONS | typeof MISSING_REASON_NO_GOALS
  }
  let masteryBySubjectId = $state<Record<string, MasteryState>>({})

  $effect(() => {
    let studentGoals: GoalDecorated[] = []
    goalsList({ query: { student: student.id } }).then(result => {
      studentGoals = result.data || []
      goalsWithCalculatedMasteryBySubjectId(student.id, studentGoals, groups).then(result => {
        let goalsBySubjectId: Record<string, GoalDecorated[]> = result
        subjects.forEach((subject: SubjectType) => {
          const goals = goalsBySubjectId[subject.id] || []
          if (goals.length > 0) {
            const masteryAggregate = aggregateMasterys(goals)
            if (masteryAggregate) {
              masteryBySubjectId[subject.id] = { mastery: masteryAggregate }
            } else {
              masteryBySubjectId[subject.id] = { missingReason: MISSING_REASON_NO_OBSERVATIONS }
            }
          } else {
            masteryBySubjectId[subject.id] = { missingReason: MISSING_REASON_NO_GOALS }
          }
        })
      })
    })
  })
</script>

<span class="item student-name">
  <a href={`/students/${student.id}`}>
    {student.name}
  </a>
</span>
{#each subjects as subject}
  <span class="item">
    {#if masteryBySubjectId[subject.id]?.mastery}
      <MasteryLevelBadge masteryData={masteryBySubjectId[subject.id].mastery!} />
    {:else if masteryBySubjectId[subject.id]?.missingReason === MISSING_REASON_NO_OBSERVATIONS}
      <MasteryLevelBadge isBadgeEmpty={true} />
    {:else if masteryBySubjectId[subject.id]?.missingReason === MISSING_REASON_NO_GOALS}
      <MasteryLevelBadge isBadgeVoid={true} />
    {:else}
      hmm
    {/if}
  </span>
{/each}

<style>
</style>
