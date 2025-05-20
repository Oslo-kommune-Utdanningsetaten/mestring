<script lang="ts">
  import StudentGoalDisplayName from './StudentGoalDisplayName.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import { dataStore } from '../stores/data'
  import { inferMastery, findAverage } from '../utils/functions'
  import type {
    Student as StudentType,
    Goal as GoalType,
    Observation as ObservationType,
  } from '../types/models'
  import { useTinyRouter } from 'svelte-tiny-router'
  const router = useTinyRouter()

  const { student, groupIds } = $props<{
    student: StudentType
    groupIds: string[]
  }>()

  let selectedGoal = $state<GoalType | null>(null)
  let isOpen = $state(false)
  const basisGroups = $derived(
    $dataStore.groups.filter(s => s.type === 'basis' && student.groupIds.includes(s.id))
  )

  const studentGoalsWithObservations = $derived(
    $dataStore.goals
      .filter((goal: GoalType) => student.goalIds.includes(goal.id))
      .sort((a, b) => {
        // sort goals by group
        if (a.groupId === b.groupId) {
          return a.title.localeCompare(b.title)
        }
        return a.groupId.localeCompare(b.groupId)
      })
      .map((goal: GoalType) => {
        const result: any = { ...goal }
        result.observations = $dataStore.observations
          .filter(o => o.goalId === goal.id && o.studentId === student.id)
          .sort((a, b) => {
            // sort observations by createdAt
            return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
          })
        result.latestObservation = result.observations[result.observations.length - 1]
        result.mastery = inferMastery(result)
        return result
      })
  )

  const masteryElements = $derived(aggregateMasteryByGroup(studentGoalsWithObservations))

  function aggregateMasteryByGroup(goals: any[]): any[] {
    const goalsByGroupId: { [key: string]: any[] } = {}
    goals.forEach(goal => {
      const { groupId } = goal
      if (!goalsByGroupId[groupId]) {
        goalsByGroupId[groupId] = []
      }
      goalsByGroupId[groupId].push(goal)
    })

    return Object.entries(goalsByGroupId).map(([groupId, goalsInGroup]) => {
      const statusValues = goalsInGroup.map((goal: any) => goal.mastery.status)
      const trendValues = goalsInGroup.map((goal: any) => goal.mastery.trend)
      return {
        groupId,
        status: findAverage(statusValues),
        trend: findAverage(trendValues),
        title: `${groupId} - aggregert`,
        groupName: goalsInGroup[0].groupId.includes('-') ? goalsInGroup[0].groupId : 'sosialt',
      }
    })
  }

  function openObservationModal(goal: GoalType) {
    selectedGoal = goal
  }
</script>

<div class="student-grid-row {isOpen ? 'is-open' : ''}">
  <div class="fw-bold">
    {student.name}
    <button class="btn border expand-student-button" onclick={() => (isOpen = !isOpen)}>
      <span class="ms-2 caret-icon {isOpen ? 'rotated' : ''}">&#9656;</span>
    </button>
  </div>
  <div>
    {basisGroups.map(g => g.name).join(', ')}
  </div>
  <div class="group-grid-columns">
    {#each groupIds.map((gid: string) => masteryElements.find(me => me.groupId === gid)) as mastery}
      <span class="group-grid-column">
        <MasteryLevelBadge {mastery} />
      </span>
    {/each}
  </div>
  <a href={`/students/${student.id}`} class="link-button">Detaljer</a>
</div>

{#if isOpen}
  {#each studentGoalsWithObservations as studentGoal, index}
    <div class="student-grid-row expanded {isOpen ? 'is-open ' : ''}">
      <StudentGoalDisplayName {studentGoal} {index} />
      <div>&nbsp;</div>
      <div class="d-flex align-items-center justify-content-start">
        <MasteryLevelBadge mastery={studentGoal.mastery} />
        {#if studentGoal.observations.length > 1}
          <div
            class="chart-container ms-2"
            title={studentGoal.observations.map((o: ObservationType) => o.masteryValue).join(', ')}
          >
            <SparklineChart
              data={studentGoal.observations.map((o: ObservationType) => o.masteryValue)}
              lineColor="rgb(100, 100, 100)"
              label={studentGoal.title}
            />
          </div>
        {:else}
          <span class="text-muted small">Ikke nok data</span>
        {/if}
      </div>
      <div>
        <button
          class="link-button px-3"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#observationOffcanvas"
          aria-controls="observationOffcanvas"
          onclick={() => openObservationModal(studentGoal)}
        >
          +
        </button>
      </div>
    </div>
  {/each}

  {#if studentGoalsWithObservations.length === 0}
    <div class="text-center text-muted py-2">Ingen mål registrert</div>
  {/if}
{/if}

<!-- Single offcanvas for observations that gets reused -->
<div
  class="offcanvas offcanvas-end offcanvas-wide"
  data-bs-scroll="true"
  tabindex="-1"
  id="observationOffcanvas"
  aria-labelledby="observationOffcanvasLabel"
>
  {#if selectedGoal}
    <div class="offcanvas-header">
      <h5 class="offcanvas-title" id="observationOffcanvasLabel">
        Ny observasjon: {selectedGoal.title}
      </h5>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="offcanvas"
        aria-label="Close"
      ></button>
    </div>
    <div class="offcanvas-body">
      <ObservationEdit {student} goal={selectedGoal} observation={null} />
    </div>
  {/if}
</div>

<style>
  .chart-container {
    padding-top: 5px;
    height: 40px;
    width: 40px;
  }

  .expand-student-button {
    padding: 2px 8px 2px 1px;
  }

  .expand-student-button:hover {
    background-color: #f8f9fa;
  }

  .caret-icon {
    display: inline-block;
    transition: transform 0.3s ease;
  }

  .rotated {
    transform: rotate(90deg);
  }

  .offcanvas-wide {
    width: 55vw !important;
  }
</style>
