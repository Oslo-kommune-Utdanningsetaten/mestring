<script lang="ts">
  import type { Mastery, GoalDecorated } from '../types/models'
  import type { UserReadable, SubjectReadable } from '../generated/types.gen'
  import { goalsList } from '../generated/sdk.gen'
  import { goalsWithCalculatedMasteryBySubjectId, aggregateMasterys } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'

  let { student, subjects } = $props<{ student: UserReadable; subjects: SubjectReadable[] }>()
  let masteryBySubjectId = $state<Record<string, Mastery | null>>({})

  $effect(() => {
    let studentGoals: GoalDecorated[] = []
    goalsList({ query: { student: student.id } }).then(result => {
      studentGoals = result.data && Array.isArray(result.data) ? result.data : []
      if (studentGoals.length > 0) {
        goalsWithCalculatedMasteryBySubjectId(student.id, studentGoals).then(result => {
          let goalsBySubjectId: Record<string, GoalDecorated[]> = result
          subjects.forEach((subject: SubjectReadable) => {
            const goals = goalsBySubjectId[subject.id] || []
            if (goals.length > 0) {
              masteryBySubjectId[subject.id] = aggregateMasterys(goals)
            }
          })
        })
      }
    })
  })
</script>

<div class="student-grid-row">
  <a href={`/students/${student.id}`}>{student.name}</a>
  <div class="group-grid-columns">
    {#each subjects as subject}
      {#if masteryBySubjectId[subject.id]}
        <MasteryLevelBadge masteryData={masteryBySubjectId[subject.id]} />
      {/if}
    {/each}
  </div>
</div>

<style>
</style>
