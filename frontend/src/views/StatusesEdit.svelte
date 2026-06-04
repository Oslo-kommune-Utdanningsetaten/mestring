<script lang="ts">
  import type { GroupType, StatusCategoryType, StatusType, UserType } from '../generated/types.gen'
  import { userGroupsList, statusList, statusCreate, statusUpdate } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { addAlert } from '../stores/alerts'
  import MasteryValueInput from '../components/MasteryValueInput.svelte'
  import { calculateSchoolYearMilestones } from '../utils/functions'
  import type { MasterySchemaWithConfig } from '../types/models'

  let { group, status_category } = $props<{
    group: GroupType
    status_category: StatusCategoryType
  }>()

  type StudentRow = {
    student: UserType
    status: StatusType | null
    masteryValue: number | null | undefined
    isSaving: boolean
    saveTimer: ReturnType<typeof setTimeout> | null
  }

  let rows = $state<StudentRow[]>([])
  let isLoading = $state(true)

  let masterySchema = $derived(
    ($dataStore.masterySchemas.find(ms => ms.id === status_category.masterySchemaId) ||
      $dataStore.defaultMasterySchema) as MasterySchemaWithConfig
  )

  const getDateRange = () => {
    const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones()
    if (status_category.name === 'midyear') {
      return { beginAt: startAt, endAt: midyearAt }
    }
    return { beginAt: startAt, endAt: endAt }
  }

  const fetchData = async () => {
    isLoading = true
    try {
      const schoolId = $dataStore.currentSchool?.id
      const userGroupsResult = await userGroupsList({
        query: { group: group.id, role: 'student', school: schoolId },
      })
      const students = (userGroupsResult.data || [])
        .map(ug => ug.user)
        .sort((a, b) => a.name.localeCompare(b.name, 'no'))

      if (students.length === 0) {
        rows = []
        return
      }

      const studentIds = students.map(s => s.id).join(',')
      const statusResult = await statusList({
        query: { students: studentIds, school: schoolId },
      })
      const allStatuses = statusResult.data || []

      rows = students.map(student => {
        const status =
          allStatuses.find(
            s => s.studentId === student.id && s.categoryId === status_category.id
          ) || null
        return {
          student,
          status,
          masteryValue: status?.masteryValue ?? null,
          isSaving: false,
          saveTimer: null,
        }
      })
    } catch (error) {
      console.error('Error fetching data:', error)
      addAlert({ type: 'danger', message: 'Noe gikk galt ved henting av elever.' })
    } finally {
      isLoading = false
    }
  }

  const saveRow = async (row: StudentRow) => {
    row.isSaving = true
    const schoolId = $dataStore.currentSchool?.id
    const dateRange = getDateRange()
    try {
      if (row.status) {
        const result = await statusUpdate({
          path: { id: row.status.id },
          body: {
            ...row.status,
            masteryValue: row.masteryValue,
          } as any,
        })
        row.status = result.data || row.status
      } else {
        const result = await statusCreate({
          body: {
            studentId: row.student.id,
            schoolId,
            categoryId: status_category.id,
            masterySchemaId: status_category.masterySchemaId,
            masteryValue: row.masteryValue,
            beginAt: dateRange.beginAt,
            endAt: dateRange.endAt,
          },
        })
        row.status = result.data || null
      }
    } catch (error) {
      console.error('Error saving status:', error)
      addAlert({
        type: 'danger',
        message: `Noe gikk galt ved lagring av status for ${row.student.name}.`,
      })
    } finally {
      row.isSaving = false
    }
  }

  const handleInputChange = (row: StudentRow) => {
    if (row.saveTimer !== null) {
      clearTimeout(row.saveTimer)
    }
    row.saveTimer = setTimeout(() => {
      row.saveTimer = null
      saveRow(row)
    }, 400)
  }

  $effect(() => {
    if (group.id && $dataStore.currentSchool?.id) {
      fetchData()
    }
  })
</script>

{#if isLoading}
  <div class="spinner-border spinner-border-sm text-primary" role="status">
    <span class="visually-hidden">Laster...</span>
  </div>
{:else if rows.length === 0}
  <p class="text-muted fst-italic">Ingen elever i denne gruppen.</p>
{:else}
  <div class="students-grid" aria-label="Elevliste">
    <div class="item header header-row student-name">Elev</div>
    <div class="item header header-row">{status_category.title}</div>

    {#each rows as row (row.student.id)}
      <div class="item student-name">
        {row.student.name}
        {#if row.isSaving}
          <span
            class="spinner-border spinner-border-sm text-primary ms-2"
            role="status"
            aria-label="Lagrer..."
          ></span>
        {/if}
      </div>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="item input-cell" onchange={() => handleInputChange(row)}>
        <MasteryValueInput {masterySchema} bind:value={row.masteryValue} />
      </div>
    {/each}
  </div>
{/if}

<style>
  .students-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
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

  .input-cell {
    align-items: start;
  }
</style>
