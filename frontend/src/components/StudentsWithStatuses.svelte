<script lang="ts">
  import type { UserType, SubjectType, StatusType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { statusList } from '../generated/sdk.gen'
  import MasterySchemaLevel from './MasterySchemaLevel.svelte'
  import UserNameLink from './UserNameLink.svelte'

  let {
    students,
    subjects,
    category,
  }: {
    students: UserType[]
    subjects: SubjectType[]
    category: string
  } = $props()

  // Sort state
  type SortKey = 'name' | string // 'name' or subjectId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

  // Data per student per subject: flat map keyed by `studentId:subjectId`
  let statusesByStudentIdAndSubjectId = $state<Record<string, StatusType[]>>({})

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
        const statusesA = statusesByStudentIdAndSubjectId[`${a.id}:${subjectId}`]
        const statusesB = statusesByStudentIdAndSubjectId[`${b.id}:${subjectId}`]
        const aggregate = sortDirection === 'asc' ? Math.min : Math.max
        const countA = statusesA?.length ? aggregate(...statusesA.map(s => s.masteryValue ?? 0)) : 0
        const countB = statusesB?.length ? aggregate(...statusesB.map(s => s.masteryValue ?? 0)) : 0
        comparison = countA - countB
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })
    return sorted
  })

  const fetchAllStudentData = async () => {
    const newData: Record<string, StatusType[]> = {}
    // Initialize empty status arrays for all students + subjects
    students.forEach(student => {
      subjects.forEach(subject => {
        newData[`${student.id}:${subject.id}`] = []
      })
    })

    const query = {
      students: students.map(s => s.id).join(','),
      school: $dataStore.currentSchool?.id,
      categoryName: category,
    }
    const result = await statusList({ query })
    const statuses = result.data || []

    statuses.forEach(status => {
      const { studentId, subjectId } = status
      if (studentId && subjectId) {
        newData[`${studentId}:${subjectId}`]?.push(status)
        statusesByStudentIdAndSubjectId = newData
      }
    })
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

  // Fetch data for all students
  $effect(() => {
    if (students.length > 0) {
      fetchAllStudentData()
    }
  })
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
        {#if subject.ownedBySchoolId}
          {subject.shortName}{getSortIndicator(subject.id)}
        {:else}
          {subject.grepCode}{getSortIndicator(subject.id)}
        {/if}
      </span>
    </button>
  {/each}
  {#each sortedStudents as student (student.id)}
    <span class="item student-name">
      <UserNameLink user={student} />
    </span>

    {#each subjects as subject}
      {@const statuses = statusesByStudentIdAndSubjectId[`${student.id}:${subject.id}`]}
      {#if statuses?.length}
        <span class="item">
          {#each statuses as status}
            <span class="me-1" title={status.title + ' i ' + subject.grepCode}>
              <MasterySchemaLevel
                masteryValue={status.masteryValue}
                masterySchemaId={status.masterySchemaId}
              />
            </span>
          {/each}
        </span>
      {:else}
        <span class="item">-</span>
      {/if}
    {/each}
  {/each}
</div>

<style>
  .students-grid {
    display: grid;
    grid-template-columns: 1.2fr repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-bottom: 1px solid var(--bs-border-color);
    min-height: 3.7rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .students-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
    max-height: 3rem;
    min-height: 2rem;
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
