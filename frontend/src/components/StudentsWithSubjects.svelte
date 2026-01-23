<script lang="ts">
  import type { UserType, SubjectType, GroupType } from '../generated/types.gen'
  import type { GoalDecorated, Mastery } from '../types/models'
  import { goalsList } from '../generated/sdk.gen'
  import {
    goalsWithCalculatedMasteryBySubjectId,
    countObservationsBySubjectId,
    aggregateMasterys,
  } from '../utils/functions'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'
  import StudentRow from './StudentRow.svelte'

  let {
    students,
    subjects,
    groups,
  }: {
    students: UserType[]
    subjects: SubjectType[]
    groups: GroupType[]
  } = $props()

  // Sort state
  type SortKey = 'name' | string // 'name' or subjectId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

  // Data per student: mastery and observation counts by subject
  type MasteryState = {
    mastery?: Mastery
    missingReason?: typeof MISSING_REASON_NO_OBSERVATIONS | typeof MISSING_REASON_NO_GOALS
  }
  type StudentData = {
    masteryBySubjectId: Record<string, MasteryState>
    observationCountBySubjectId: Record<string, number>
  }
  let dataByStudentId = $state<Record<string, StudentData>>({})

  // Fetch data for all students
  $effect(() => {
    const fetchAllStudentData = async () => {
      const newData: Record<string, StudentData> = {}

      await Promise.all(
        students.map(async student => {
          const result = await goalsList({
            query: { student: student.id, includeObservations: true },
          })
          const studentGoals = result.data || []

          const goalsBySubjectId = await goalsWithCalculatedMasteryBySubjectId(
            student.id,
            studentGoals,
            groups
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
        })
      )

      dataByStudentId = newData
    }

    if (students.length > 0) {
      fetchAllStudentData()
    }
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
</script>

<div class="students-grid" aria-label="Elevliste" style="--columns-count: {subjects.length}">
  <button
    class="item header header-row sortable"
    onclick={() => handleHeaderClick('name')}
    title="Sorter etter elevnavn"
  >
    Elev{getSortIndicator('name')}
  </button>
  {#each subjects as subject (subject.id)}
    <button
      class="item header header-row sortable"
      onclick={() => handleHeaderClick(subject.id)}
      title="Sorter etter antall observasjoner i {subject.displayName}"
    >
      <span class="column-header">
        {subject.shortName}{getSortIndicator(subject.id)}
      </span>
    </button>
  {/each}
  {#each sortedStudents as student (student.id)}
    <StudentRow
      {student}
      {subjects}
      masteryBySubjectId={dataByStudentId[student.id]?.masteryBySubjectId}
    />
  {/each}
</div>

<style>
  .students-grid {
    display: grid;
    grid-template-columns: minmax(180px, 2fr) repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-bottom: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .students-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
    max-height: 4rem;
  }

  .students-grid :global(.item.header:first-child),
  .students-grid :global(.item.student-name) {
    justify-content: flex-start;
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

  .column-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
    padding: 0.1rem 0.3rem 0.1rem 0.3rem;
    max-width: 6rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border: 1px solid var(--pkt-color-grays-gray-100);
    overflow-wrap: break-word;
  }
</style>
