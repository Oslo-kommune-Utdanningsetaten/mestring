<script lang="ts">
  import type { Mastery, GoalDecorated } from '../types/models'
  import type { UserReadable, SubjectReadable } from '../api/types.gen'
  import { calculateMasterysForStudent, findAverage } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'

  let { student, subjects } = $props<{ student: UserReadable; subjects: SubjectReadable[] }>()
  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let masteryBySubjectId = $state<Record<string, Mastery>>({})

  function aggregateMasterys(goals: GoalDecorated[]): Mastery {
    console.log('Aggggggg --->', goals)
    const masteryValues = goals.map((goal: any) => goal.masteryData.mastery)
    const trendValues = goals.map((goal: any) => goal.masteryData.trend)
    return {
      mastery: findAverage(masteryValues),
      trend: findAverage(trendValues),
      title: `Aggregert for ${goals.length} mål`,
    }
  }

  $effect(() => {
    calculateMasterysForStudent(student.id).then(result => {
      console.log(`Calculating - student ${student.id}`)
      goalsBySubjectId = result
      console.log(`Calculating - goals`, goalsBySubjectId)
      subjects.forEach((subject: SubjectReadable) => {
        const goals = goalsBySubjectId[subject.id] || []
        console.log(`Found ${goals.length} goals for subject ${subject.id}`)
        // The problem is that if there is no mastery data, the aggregateMasterys function crashes. Maybe not call it at all?
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
