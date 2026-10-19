<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type { UserType, SubjectType, StatusType, GroupType } from '../generated/types.gen'
  import type { MasteryConfigLevel } from '../types/models.d.ts'
  import { statusList } from '../generated/sdk.gen'
  import { dataStore, currentUser } from '../stores/data'
  import { getGroupLabel, getSubjectName } from '../utils/functions'
  import { getPreferredCreatedParams } from '../stores/localStorageFunctions'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { t } from '../stores/translations'

  import MasterySchemaLevel from './MasterySchemaLevel.svelte'
  import UserNameLink from './UserNameLink.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import GroupTag from './GroupTag.svelte'

  let {
    students,
    subjects,
    categoryName,
    group,
  }: {
    students: UserType[]
    subjects: SubjectType[]
    categoryName: string
    group?: GroupType | undefined
  } = $props()

  type DecoratedGroup = GroupType & {
    studentCount: number
    statusCount: number
  }

  // Sort state
  type SortKey = 'name' | string // 'name' or subjectId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

  // Data per student per subject: flat map keyed by `studentId:subjectId`
  let statusesByStudentIdAndSubjectId = $state<Record<string, StatusType[]>>({})
  let studentCountsByLevel = $state<number[]>([])

  let selectedLevels = $state<number[]>([])
  let isDetailsEnabled = $derived<boolean>(!!group || selectedLevels.length > 0)

  // Top scrollbar mirror
  let gridElement = $state<HTMLDivElement | null>(null)
  let topScrollElement = $state<HTMLDivElement | null>(null)
  let gridScrollWidth = $state(0)

  const gridTemplateColumns = $derived(
    ['minmax(12rem, 1.2fr)', ...subjects.map(() => 'minmax(8rem, 1fr)')].join(' ')
  )

  const category = $derived($dataStore.statusCategories.find(cat => cat.name === categoryName))
  const masterySchema = $derived(
    $dataStore.masterySchemas.find(schema => schema.id === category?.masterySchemaId)
  )
  const { maxValue } = $derived(useMasteryCalculations(masterySchema))

  // Sorted students list
  let sortedStudents = $derived.by(() => {
    let result = [...students]
    if (selectedLevels.length > 0) {
      result = result.filter(student =>
        subjects.some(subject => {
          const statuses = statusesByStudentIdAndSubjectId[`${student.id}:${subject.id}`]
          return statuses?.some(status => {
            return selectedLevels.some(
              levelIndex => getValueForIndex(levelIndex) === status?.masteryValue
            )
          })
        })
      )
    }
    result.sort((a, b) => {
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
    return result
  })

  const studentsWithouRiskyStatuses = $derived.by(() => {
    return students.filter(student =>
      subjects.every(subject => {
        const statuses = statusesByStudentIdAndSubjectId[`${student.id}:${subject.id}`] || []
        return (
          statuses.filter(status => status.masteryValue === maxValue).length === statuses.length
        )
      })
    )
  })

  const decoratedGroups: DecoratedGroup[] = $derived.by(() => {
    const subjectIds = subjects.map(aSubject => aSubject.id)
    return $currentUser.allGroups
      .filter((aGroup: GroupType) => aGroup.subjectId && aGroup.type === 'teaching')
      .filter((aGroup: GroupType) => subjectIds.includes(aGroup.subjectId as string))
      .map((aGroup: GroupType) => {
        const studentsInGroup = students.filter(student => student.groupIds.includes(aGroup.id))
        return {
          ...aGroup,
          studentCount: studentsInGroup.length,
          // Group only counts statuses in its own subject
          statusCount: studentsInGroup.reduce(
            (count, student) =>
              count +
              (statusesByStudentIdAndSubjectId[`${student.id}:${aGroup.subjectId}`]?.length ?? 0),
            0
          ),
        }
      })
  })

  const groupsMissingStatuses = $derived(
    decoratedGroups.filter((aGroup: DecoratedGroup) => aGroup.statusCount < aGroup.studentCount)
  )

  const groupsWithCompleteStatuses = $derived(
    decoratedGroups.filter((aGroup: DecoratedGroup) => aGroup.statusCount >= aGroup.studentCount)
  )

  const getStudentCountWithoutRiskyStatuses = (): number => {
    if (selectedLevels.length > 0) return 0
    return studentsWithouRiskyStatuses.length
  }

  const getValueForIndex = (levelIndex: number): number => {
    return masterySchema.config.levels[levelIndex]?.maxValue
  }

  const fetchAllStudentData = async () => {
    const newData: Record<string, StatusType[]> = {}
    // Initialize empty status arrays for all students + subjects
    students.forEach(student => {
      subjects.forEach(subject => {
        newData[`${student.id}:${subject.id}`] = []
      })
    })

    const query = {
      group: group ? group.id : undefined,
      school: $dataStore.currentSchool?.id,
      categoryName: categoryName,
      ...getPreferredCreatedParams(),
    }
    const result = await statusList({ query })
    const statuses = result.data || []

    // Build data stucture for lookup of statuses by student and subject
    statuses.forEach(status => {
      const { studentId, subjectId } = status
      if (studentId && subjectId) {
        newData[`${studentId}:${subjectId}`]?.push(status)
        statusesByStudentIdAndSubjectId = newData
      }
    })

    // Build student counts by mastery level
    studentCountsByLevel = masterySchema.config.levels.map(
      (level: MasteryConfigLevel) =>
        students.filter(student =>
          subjects.some(subject =>
            newData[`${student.id}:${subject.id}`].some(
              status => status.masteryValue === level.maxValue
            )
          )
        ).length
    )
  }

  const handleToggleLevel = (levelIndex: number) => {
    if (selectedLevels.includes(levelIndex)) {
      selectedLevels = selectedLevels.filter(index => index !== levelIndex)
    } else {
      selectedLevels = [...selectedLevels, levelIndex]
    }
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

  $effect(() => {
    if (!gridElement) return
    const obs = new ResizeObserver(() => {
      gridScrollWidth = gridElement!.scrollWidth
    })
    obs.observe(gridElement)
    return () => obs.disconnect()
  })

  // Fetch data for all students
  $effect(() => {
    if (students.length > 0) {
      fetchAllStudentData()
    }
  })
</script>

<div>👉 Velg gruppe og/eller filter for å se detaljer</div>

<!-- Filtering by mastery level -->
{#if masterySchema && category}
  {@const levels =
    category.name === 'risk'
      ? masterySchema.config.levels.slice(0, -1)
      : masterySchema.config.levels}
  <table class="my-2 table">
    <thead>
      <tr>
        <th></th>
        <th>Antall</th>
        <th>Filter</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>Elever {group ? `i dette utvalget` : 'på hele skolen'}</th>
        <td>{sortedStudents.length}</td>
        <td></td>
      </tr>
      {#if category.name === 'risk'}
        <tr>
          <th>Elever {group ? `i dette utvalget` : 'på hele skolen'} utenfor fare</th>
          <td>
            {getStudentCountWithoutRiskyStatuses()} [{Math.round(
              (getStudentCountWithoutRiskyStatuses() / sortedStudents.length) * 100
            )}%]
          </td>
          <td></td>
        </tr>
      {/if}
      {#each levels as level, levelIndex}
        <tr>
          <th>Elever med én eller flere {level.title}</th>
          <td>{studentCountsByLevel[levelIndex] ?? 0}</td>
          <td>
            <pkt-checkbox
              label={''}
              aria-label="Filter for level {level.title}"
              labelPosition="right"
              layout="horizontal"
              checked={selectedLevels.includes(levelIndex)}
              onchange={() => handleToggleLevel(levelIndex)}
            ></pkt-checkbox>
          </td>
        </tr>
      {/each}

      {#if !group}
        <tr>
          <th>Grupper som har rapportert alle elever</th>
          <td>
            <div class="d-flex flex-wrap gap-1">
              {#each groupsWithCompleteStatuses as group}
                <GroupTag
                  href="/groups/{group.id}"
                  {group}
                  isGroupNameEnabled={true}
                  isIconEnabled={false}
                />
              {/each}
            </div>
          </td>
          <td></td>
        </tr>
        <tr>
          <th>Grupper som ikke har rapportert alle elever</th>
          <td>
            <div class="d-flex flex-wrap gap-1">
              {#each groupsMissingStatuses as group}
                <GroupTag
                  href="/groups/{group.id}"
                  {group}
                  isGroupNameEnabled={true}
                  isIconEnabled={false}
                />
              {/each}
            </div>
          </td>
          <td></td>
        </tr>
      {/if}
    </tbody>
  </table>
{/if}

<div class="mt-3">
  {#if isDetailsEnabled}
    <!-- Students grid -->
    <p>Viser {sortedStudents.length} elev{sortedStudents.length === 1 ? '' : 'er'}</p>
    <div class="scroll-mirror" bind:this={topScrollElement} onscroll={syncFromTop}>
      <div style="width: {gridScrollWidth}px; height: 1px;"></div>
    </div>
    <div
      class="students-grid"
      bind:this={gridElement}
      onscroll={syncFromGrid}
      aria-label="Elevliste"
      style="grid-template-columns: {gridTemplateColumns}"
    >
      <button
        class="item header header-row sortable"
        onclick={() => handleHeaderClick('name')}
        title="Sorter etter elevnavn"
      >
        <span class="column-header">
          Navn{getSortIndicator('name')}
        </span>
      </button>
      {#each subjects as subject (subject.id)}
        <button
          class="item header header-row sortable"
          onclick={() => handleHeaderClick(subject.id)}
          title="Sorter etter antall {t('status', { form: 'plu-indef' })} i {getSubjectName(
            subject
          )}"
        >
          <span class="column-header">
            {getSubjectName(subject)}{getSortIndicator(subject.id)}
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
  {/if}
</div>

<style>
  .scroll-mirror {
    overflow-x: auto;
    overflow-y: hidden;
  }

  .students-grid {
    display: grid;
    overflow-x: auto;
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
    padding: 0.3rem;
    background-color: var(--bs-light);
    font-weight: 800;
    align-self: stretch;
    align-items: stretch;
    min-height: 2.5rem;
    position: sticky;
    top: 0;
    z-index: 10;
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
    display: flex;
    align-items: center;
    justify-content: center;
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
