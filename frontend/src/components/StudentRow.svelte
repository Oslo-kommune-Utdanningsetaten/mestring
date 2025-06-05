<script lang="ts">
  import type { Mastery, GoalDecorated } from '../types/models'
  import type { UserReadable, SubjectReadable } from '../api/types.gen'
  import { calculateMasterysForStudent, findAverage, isNumber } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'

  let { student, subjects } = $props<{ student: UserReadable; subjects: SubjectReadable[] }>()
  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let masteryBySubjectId = $state<Record<string, Mastery | null>>({})

  function aggregateMasterys(goals: GoalDecorated[]): Mastery | null {
    const masteryValues: number[] = []
    const trendValues: number[] = []
    goals.forEach(goal => {
      if (isNumber(goal.masteryData?.mastery)) {
        masteryValues.push(goal.masteryData.mastery)
      }
      if (isNumber(goal.masteryData?.trend)) {
        trendValues.push(goal.masteryData.trend)
      }
    })
    // if there are no mastery values, there will not be a trend either
    if (masteryValues.length === 0) {
      return null
    }
    return {
      mastery: findAverage(masteryValues),
      trend: findAverage(trendValues),
      title: `Aggregert: ${masteryValues.length}/${goals.length} mål har data`,
    }
  }

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
  <a href={`/students/${student.id}`} class="fw-bold">{student.name}</a>
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
