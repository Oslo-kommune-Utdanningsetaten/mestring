<script lang="ts">
  import type { UserType, SubjectType, GroupType } from '../generated/types.gen'
  import type { MasteryData, MasteryState } from '../types/models'
  import { dataStore } from '../stores/data'
  import { goalsList } from '../generated/sdk.gen'
  import {
    goalsWithCalculatedMasteryBySubjectId,
    countObservationsBySubjectId,
    aggregateMasterys,
  } from '../utils/functions'
  import { localStorage } from '../stores/localStorage'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import UserNameLink from './UserNameLink.svelte'
  import StudentSubjectChart from './StudentSubjectChart.svelte'

  let {
    students,
    subjects,
    group,
  }: {
    students: UserType[]
    subjects: SubjectType[]
    group?: GroupType
  } = $props()

  const allGroups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  // Only display polar chart if students list is scoped -> avoids performance issues
  const polarChartStore = localStorage<boolean>('isSubjectPolarChartVisible')
  const isSubjectPolarChartVisible = $derived(!!group && ($polarChartStore ?? false))

  // Sort state
  type SortKey = 'name' | string // 'name' or subjectId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

  // Top scrollbar mirror
  let gridElement = $state<HTMLDivElement | null>(null)
  let topScrollElement = $state<HTMLDivElement | null>(null)
  let gridScrollWidth = $state(0)

  // Data per student: mastery and observation counts by subject
  type StudentData = {
    masteryBySubjectId: Record<string, MasteryState>
    observationCountBySubjectId: Record<string, number>
  }
  let dataByStudentId = $state<Record<string, StudentData>>({})

  // Compute grid template columns
  const gridTemplateColumns = $derived.by(() => {
    const nameCol = 'minmax(6rem, 10rem)'
    const normalCol = '7.2rem'
    const cols: string[] = [nameCol]
    subjects.forEach(() => cols.push(normalCol)) // one column per subject
    return cols.join(' ')
  })

  // Sorted students list
  let sortedStudents = $derived.by(() => {
    const sorted = [...students]
    sorted.sort((a, b) => {
      let comparison: number
      if (sortBy === 'name') {
        comparison = a.name.localeCompare(b.name, 'no')
      } else {
        // sortBy contains a subjectId when not sorting by name
        const subjectId = sortBy
        const countA = dataByStudentId[a.id]?.observationCountBySubjectId[subjectId] ?? 0
        const countB = dataByStudentId[b.id]?.observationCountBySubjectId[subjectId] ?? 0
        comparison = countA - countB
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })
    return sorted
  })

  const fetchAllStudentData = async () => {
    const newData: Record<string, StudentData> = {}

    await Promise.all(
      students.map(async student => {
        const result = await goalsList({
          query: {
            student: student.id,
            includeObservations: true,
            school: $dataStore.currentSchool?.id,
          },
        })
        const studentGoals = result.data || []

        const goalsBySubjectId = await goalsWithCalculatedMasteryBySubjectId(
          student.id,
          studentGoals,
          allGroups
        )
        const masteryBySubjectId: Record<string, MasteryState> = {}
        subjects.forEach(subject => {
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

        const observationCountBySubjectId = countObservationsBySubjectId(goalsBySubjectId)

        newData[student.id] = {
          masteryBySubjectId,
          observationCountBySubjectId,
        }
        dataByStudentId = newData
      })
    )
  }

  const handleHeaderClick = (key: SortKey) => {
    if (sortBy === key) {
      // Toggle direction
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      // New sort key
      sortBy = key
      sortDirection = key === 'name' ? 'asc' : 'desc' // Default: name asc, observations desc
    }
  }

  const getSortIndicator = (key: SortKey): string => {
    if (sortBy !== key) return ''
    return sortDirection === 'asc' ? ' ▲' : ' ▼'
  }

  const syncFromGrid = () => {
    if (topScrollElement && gridElement) topScrollElement.scrollLeft = gridElement.scrollLeft
  }

  const syncFromTop = () => {
    if (gridElement && topScrollElement) gridElement.scrollLeft = topScrollElement.scrollLeft
  }

  // Fetch data for all students
  $effect(() => {
    if (students.length > 0) {
      fetchAllStudentData()
    }
  })

  $effect(() => {
    if (!gridElement) return
    const obs = new ResizeObserver(() => {
      gridScrollWidth = gridElement!.scrollWidth
    })
    obs.observe(gridElement)
    return () => obs.disconnect()
  })
</script>

{#snippet studentRow(student: UserType, masteryBySubjectId: any)}
  <span class="item student-name">
    <UserNameLink user={student} />
  </span>

  {#each subjects as subject}
    <span class="item">
      {#if isSubjectPolarChartVisible}
        <div class="chart-wrapper">
          <StudentSubjectChart {student} {subject} />
        </div>
      {/if}
      {#if masteryBySubjectId?.[subject.id]}
        <MasteryLevelBadge
          masteryData={masteryBySubjectId[subject.id].mastery!}
          masterySchema={$dataStore.defaultMasterySchema}
          dataMissingReason={masteryBySubjectId[subject.id].missingReason}
        />
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
{/snippet}

<div class="scroll-mirror" bind:this={topScrollElement} onscroll={syncFromTop}>
  <div style="width: {gridScrollWidth}px; height: 1px;"></div>
</div>
<div
  class="students-grid"
  bind:this={gridElement}
  onscroll={syncFromGrid}
  style="grid-template-columns: {gridTemplateColumns}"
  aria-label="Elevliste"
>
  <span class="item header header-row">
    <button
      class="column-header-button sortable"
      onclick={() => handleHeaderClick('name')}
      title="Sorter etter elevnavn"
    >
      Navn{getSortIndicator('name')}
    </button>
  </span>

  {#each subjects as subject (subject.id)}
    {@const subjectName =
      subject.shortName || subject.displayName || subject.grepCode || 'ukjent fag'}

    <span class="item header header-row">
      <button
        class="column-header-button sortable"
        onclick={() => handleHeaderClick(subject.id)}
        title="Sorter etter antall observasjoner i {subject.grepCode}"
      >
        {subjectName}{getSortIndicator(subject.id)}
      </button>
    </span>
  {/each}
  {#each sortedStudents as student (student.id)}
    {@render studentRow(student, dataByStudentId[student.id]?.masteryBySubjectId)}
  {/each}
</div>

<style>
  .chart-wrapper {
    width: 32px;
    height: 32px;
  }

  .scroll-mirror {
    overflow-x: auto;
    overflow-y: hidden;
  }

  .students-grid {
    display: grid;
    align-items: start;
    gap: 0;
    overflow-x: auto;
  }

  .students-grid .item {
    padding: 0.5rem;
    min-height: 3.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow-y: hidden;
    gap: 0.5rem;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
  }

  .students-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .students-grid .item.header {
    border-top: 1px solid var(--bs-border-color);
  }

  .students-grid .item.header:first-child,
  .students-grid .item.student-name {
    justify-content: flex-start;
    border-left: 1px solid var(--bs-border-color);
  }

  .sortable {
    cursor: pointer;
    border: none;
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .sortable:hover {
    background-color: var(--bs-gray-300);
  }

  .column-header-button {
    overflow-wrap: break-word;
    width: 100%;
    font-size: 0.8rem;
    padding: 0.1rem 0.5rem 0.1rem 0.5rem;
    background-color: color-mix(
      in srgb,
      var(--pkt-color-surface-strong-light-green) 70%,
      transparent
    );
    border: 1px solid var(--pkt-color-grays-gray-100);
    z-index: 2;
  }
</style>
