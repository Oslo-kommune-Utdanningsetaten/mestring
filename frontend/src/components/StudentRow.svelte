<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import StudentStatus from './StudentStatus.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import { dataStore } from '../stores/data'
  import type {
    Student as StudentType,
    Goal as GoalType,
    Observation as ObservationType,
  } from '../types/models'
  const router = useTinyRouter()

  const { student } = $props<{ student: StudentType }>()
  let isOpen = $state(false)

  const subjects = $derived($dataStore.subjects)
  const groups = $derived($dataStore.groups)

  const studentGoals = $derived(
    student.goalIds.map((goalId: string) => $dataStore.goals.find(g => g.id === goalId))
  )

  const studentGoalsWithObservations = $derived(
    studentGoals.map((goal: GoalType): object => {
      const result: any = { ...goal }
      result.observations = $dataStore.observations
        .filter(o => o.goalId === goal.id)
        .sort((a, b) => {
          return new Date(a.date).getTime() - new Date(b.date).getTime()
        })
      return result
    })
  )
</script>

<div class="row py-2 align-items-center mx-0 border-top {isOpen ? '' : 'border-bottom'} ">
  <div class="col-3 fw-bold">
    <a onclick={() => (isOpen = !isOpen)}>
      {student.name}
    </a>
  </div>
  <div class="col-3 text-center"><StudentStatus {studentGoals} /></div>
  <div class="col-2 text-center">
    {groups.find(g => g.id === student.groupId)?.name || ''}
  </div>
  <div class="col-2 text-center">
    {$dataStore.goals.filter(g => g.studentId === student.id).length}
  </div>
  <div class="col-2">
    <div class="d-flex gap-2 justify-content-center">
      <a href={`/students/${student.id}`} class="link-button">Detaljer</a>
    </div>
  </div>
</div>

{#if isOpen}
  {#each studentGoalsWithObservations as goal}
    <div class="row align-items-center border-top py-1 mx-0 expanded-student-row">
      <div class="col-4">
        <span class="fw-medium">{goal.title}</span>
      </div>
      <div class="col-2 chart-container">
        {#if goal.observations.length > 0}
          <SparklineChart
            data={goal.observations.map((o: ObservationType) => o.masteryValue)}
            lineColor="rgb(75, 192, 192)"
            label={goal.title}
          />
        {:else}
          <div class="text-muted small">Ingen data</div>
        {/if}
      </div>
      <div class="col-2"></div>
      <div class="col-2"></div>
      <div class="col-2"></div>
    </div>
  {/each}

  {#if studentGoalsWithObservations.length === 0}
    <div class="text-center text-muted py-2">Ingen mål registrert</div>
  {/if}
{/if}

<style>
  .chart-container {
    padding-top: 5px;
    height: 40px;
    width: 80px;
  }
  .expanded-student-row {
    background-color: #f8f9fa;
  }
</style>
