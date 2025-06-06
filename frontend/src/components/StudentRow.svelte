<script lang="ts">
  import type { Mastery, GoalDecorated } from '../types/models'
  import type { UserReadable, SubjectReadable } from '../api/types.gen'
  import { calculateMasterysForStudent, aggregateMasterys } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'

  let { student, subjects } = $props<{ student: UserReadable; subjects: SubjectReadable[] }>()
  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let masteryBySubjectId = $state<Record<string, Mastery | null>>({})

  $effect(() => {
    calculateMasterysForStudent(student.id).then(result => {
      goalsBySubjectId = result
      subjects.forEach((subject: SubjectReadable) => {
        const goals = goalsBySubjectId[subject.id] || []
        if (goals.length > 0) {
          masteryBySubjectId[subject.id] = aggregateMasterys(goals)
        }
      })
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
