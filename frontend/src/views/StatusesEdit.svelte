<script lang="ts">
  import type { GroupType, StatusCategoryType, StatusType, UserType } from '../generated/types.gen'
  import {
    usersList,
    statusList,
    statusCreate,
    statusUpdate,
    statusDestroy,
  } from '../generated/sdk.gen'
  import { hasUserAccessToFeature } from '../stores/access'
  import { calculateSchoolYearMilestones, generateStatusTitle } from '../utils/functions'
  import { dataStore } from '../stores/data'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  import MasteryValueInput from '../components/MasteryValueInput.svelte'
  import ButtonIcon from '../components/ButtonIcon.svelte'
  import Status from './Status.svelte'

  let { groupId, statusCategoryName } = $props<{
    groupId: string
    statusCategoryName: string
  }>()

  type RowType = {
    isSaving: boolean
    saveTimer: ReturnType<typeof setTimeout> | null
  }

  let rows = $state<RowType[]>([])

  let group = $state<GroupType | null>(
    $dataStore.currentUser.allGroups.find((group: GroupType) => group.id === groupId) || null
  )
  let students = $state<UserType[]>([])
  let isLoading = $state(true)
  let statusesByStudentId = $state<Record<string, StatusType[]>>({})

  let statusCategory = $derived<StatusCategoryType | null>(
    $dataStore.statusCategories.find(sc => sc.name === statusCategoryName) || null
  )

  const getDateRange = () => {
    const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones()
    if (statusCategory?.name === 'midyear') {
      return { beginAt: startAt, endAt: midyearAt }
    }
    return { beginAt: startAt, endAt: endAt }
  }

  const fetchData = async () => {
    if (!group || !statusCategory) {
      return
    }
    isLoading = true
    try {
      const schoolId = $dataStore.currentSchool?.id
      const usersResult = await usersList({
        query: { groups: groupId, roles: 'student', school: schoolId },
      })
      students = (usersResult.data || []).sort((a: UserType, b: UserType) =>
        a.name.localeCompare(b.name, 'no')
      )

      if (students.length === 0) {
        isLoading = false
        return
      }

      const statusResult = await statusList({
        query: { group: groupId, school: schoolId, categoryName: statusCategoryName },
      })
      const allStatuses = statusResult.data || []
      // TODO: Filter statuses by date range (beginAt/endAt) to get current statuses only

      students.forEach(student => {
        const statuses =
          allStatuses.filter(
            status => status.studentId === student.id && status.categoryId === statusCategory.id
          ) || []
        rows.push({ isSaving: false, saveTimer: null })
        if (statuses.length === 0) {
          const statusWip = {
            studentId: student.id,
            categoryId: statusCategory.id,
            masterySchemaId: statusCategory.masterySchemaId,
            masteryValue: null,
            beginAt: getDateRange().beginAt,
            endAt: getDateRange().endAt,
          } as StatusType
          statusWip.title = generateStatusTitle(statusWip, statusCategory)
          statuses.push(statusWip)
        }
        statusesByStudentId = { ...statusesByStudentId, [student.id]: statuses }
      })
    } catch (error) {
      console.error('Error fetching data:', error)
      addAlert({ type: 'danger', message: 'Noe gikk galt ved henting av data' })
    } finally {
      isLoading = false
    }
  }

  const storeStatus = async (status: Partial<StatusType>, row: RowType) => {
    row.isSaving = true
    try {
      if (status.id) {
        await statusUpdate({
          path: { id: status.id },
          body: {
            ...status,
          } as StatusType,
        })
      } else {
        await statusCreate({
          body: {
            ...status,
          } as StatusType,
        })
      }
      await fetchData() // Refresh data after save to get updated list of statuses with ids
    } catch (error) {
      console.error('Error saving status:', error)
      addAlert({
        type: 'danger',
        message: `Noe gikk galt ved lagring av status ${statusCategory?.name} for elev ${status.studentId}.`,
      })
    } finally {
      row.isSaving = false
    }
  }

  const handleChangeStatus = (status: Partial<StatusType>, rowIndex: number) => {
    const row = rows[rowIndex]
    if (row.saveTimer !== null) {
      clearTimeout(row.saveTimer)
    }
    row.saveTimer = setTimeout(() => {
      row.saveTimer = null
      storeStatus(status, row)
    }, 400)
  }

  const handleDeleteStatus = async (status: StatusType) => {
    if (!status) return
    try {
      await statusDestroy({ path: { id: status.id } })
      trackEvent('Status', 'Delete')

      addAlert({
        type: 'success',
        message: `Slettet status "${status.title}"`,
      })
    } catch (error) {
      console.error('Error deleting status:', error)
      addAlert({
        type: 'danger',
        message: `Kunne ikke slette status "${status.title}". Hvis du mener dette er en feil, kontakt support.`,
      })
    }
    await fetchData()
  }

  $effect(() => {
    if (group && statusCategory) {
      fetchData()
    }
  })
</script>

<section>
  <h2>Statuser</h2>
  {#if group && statusCategory}
    {#if group.subjectId}
      {#if isLoading}
        <div class="spinner-border spinner-border-sm text-primary" role="status">
          <span class="visually-hidden">Henter data...</span>
        </div>
      {:else if students.length === 0}
        <p>Fant ingen elever i denne gruppen.</p>
      {:else}
        <div class="students-grid" aria-label="Elevliste">
          <span class="item header-row-item">Elev</span>
          <span class="item header-row-item">{statusCategory.title}</span>

          {#each students as student, index (student.id)}
            <span class="item student-name">{student.name}</span>
            <span class="item">
              {#each statusesByStudentId[student.id] as status (status.id)}
                {@const masterySchema = $dataStore.masterySchemas.find(
                  ms => ms.id === status.masterySchemaId
                )}
                <div
                  class="mastery-input-container"
                  onchange={() => handleChangeStatus(status, index)}
                >
                  {status.title} [{status.id}]
                  {#if status.id && $hasUserAccessToFeature( 'status', 'delete', { groupId, createdById: status.createdById } )}
                    {#key status.id}
                      <ButtonIcon
                        options={{
                          iconName: 'trash-can',
                          title: 'Slett status',
                          classes: 'bordered',
                          onClick: () => handleDeleteStatus(status),
                          delayActionFor: 3,
                        }}
                      />
                    {/key}
                  {/if}
                  <MasteryValueInput {masterySchema} bind:value={status.masteryValue} />
                </div>
              {/each}
            </span>
          {/each}
        </div>
      {/if}
    {:else}
      <p>
        Gruppa {group.displayName} har ingen fagtilknytning, og elevene kan derfor ikke tilordnes status.
      </p>
    {/if}
  {:else}
    <p>Gruppe: {group?.id}</p>
    <p>Statuskategori: {statusCategory?.id}</p>
  {/if}
</section>

<style>
  .students-grid {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    align-items: stretch;
    gap: 0;
  }

  .students-grid .item {
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
  }

  .students-grid .item.header-row-item {
    background-color: var(--bs-light);
    font-weight: 800;
    border-top: 1px solid var(--bs-border-color);
  }

  .students-grid .item:first-child,
  .students-grid .item.student-name {
    justify-content: flex-start;
    border-left: 1px solid var(--bs-border-color);
  }

  .mastery-input-container {
    width: 100%;
  }
</style>
