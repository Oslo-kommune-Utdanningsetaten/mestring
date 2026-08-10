<script lang="ts">
  import type {
    GroupType,
    StatusCategoryType,
    StatusType,
    UserType,
    SubjectType,
  } from '../generated/types.gen'
  import {
    usersList,
    statusList,
    statusCreate,
    statusUpdate,
    statusDestroy,
  } from '../generated/sdk.gen'
  import { hasUserAccessToFeature } from '../stores/access'
  import {
    calculateSchoolYearMilestones,
    generateStatusTitle,
    getDateSpanForStatusCategory,
    getPreferredCreatedParams,
  } from '../utils/functions'
  import { dataStore } from '../stores/data'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  import MasteryValueInput from '../components/MasteryValueInput.svelte'
  import ButtonIcon from '../components/ButtonIcon.svelte'
  import AuthorInfo from '../components/AuthorInfo.svelte'
  import Link from '../components/Link.svelte'
  import StatusEdit from '../components/StatusEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'

  let { groupId, statusCategoryName } = $props<{
    groupId: string
    statusCategoryName: string
  }>()

  type RowType = {
    isSaving: boolean
    studentId: string | undefined
  }

  let rows = $state<RowType[]>([])

  let group = $state<GroupType | null>(
    $dataStore.currentUser.allGroups.find((group: GroupType) => group.id === groupId) || null
  )
  const subject = $derived<SubjectType | undefined>(
    $dataStore.subjects.find(s => s.id === group?.subjectId)
  )

  let students = $state<UserType[]>([])
  let isLoading = $state(true)
  let statusesByStudentId = $state<Record<string, StatusType[]>>({})
  let statusWip = $state<StatusType | null>(null)
  let isStatusEditorOpen = $state(false)

  let statusCategory = $derived<StatusCategoryType | undefined>(
    $dataStore.statusCategories.find(sc => sc.name === statusCategoryName) || undefined
  )

  const getDateRange = () => {
    const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones()
    if (statusCategory?.name === 'midyear') {
      return { beginAt: startAt, endAt: midyearAt }
    }
    return { beginAt: startAt, endAt: endAt }
  }

  const fetchData = async () => {
    if (!group || !statusCategory || !subject) {
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
        query: {
          group: groupId,
          subject: subject.id,
          school: schoolId,
          categoryName: statusCategoryName,
          ...getPreferredCreatedParams(),
        },
      })
      const allStatuses = statusResult.data || []

      const { beginAt, endAt } = getDateSpanForStatusCategory(statusCategory.name)
      students.forEach(student => {
        const statuses =
          allStatuses
            .filter(status => status.studentId === student.id)
            .filter(status => status.categoryId === statusCategory.id)
            .filter(
              status =>
                status.beginAt.split('T')[0] === beginAt && status.endAt.split('T')[0] === endAt
            ) || []
        rows.push({ isSaving: false, studentId: student.id })
        if (statuses.length === 0) {
          statuses.push(getNewStatus(student.id))
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

  const getNewStatus = (studentId: string) => {
    const newStatus = {
      studentId: studentId,
      subjectId: group?.subjectId,
      categoryId: statusCategory?.id,
      masterySchemaId: statusCategory?.masterySchemaId,
      masteryValue: null,
      schoolId: $dataStore.currentSchool?.id,
      beginAt: getDateRange().beginAt,
      endAt: getDateRange().endAt,
    } as StatusType
    newStatus.title = generateStatusTitle(newStatus, statusCategory)
    return newStatus
  }

  const refetchDataForRow = async (studentId: string) => {
    if (!group || !subject || !studentId) return
    const statusResult = await statusList({
      query: {
        group: groupId,
        students: studentId,
        subject: subject.id,
        school: $dataStore.currentSchool?.id,
        categoryName: statusCategoryName,
        ...getPreferredCreatedParams(),
      },
    })
    const studenStatuses = statusResult.data || []
    if (studenStatuses.length === 0) {
      studenStatuses.push(getNewStatus(studentId))
    }

    statusesByStudentId = { ...statusesByStudentId, [studentId]: studenStatuses }
  }

  const createOrUpdateStatus = async (status: Partial<StatusType>, rowIndex: number) => {
    const row = rows[rowIndex]
    row.isSaving = true

    try {
      if (status.id) {
        await statusUpdate({
          path: { id: status.id },
          body: {
            ...status,
          } as StatusType,
        })
        trackEvent('Status', 'Update')
      } else {
        await statusCreate({
          body: {
            ...status,
          } as StatusType,
        })
        trackEvent('Status', 'Create')
      }
      await refetchDataForRow(status.studentId as string)
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

  const handleChangeStatus = async (status: Partial<StatusType>, rowIndex: number) => {
    await createOrUpdateStatus(status, rowIndex)
  }

  const handleDeleteStatus = async (status: StatusType) => {
    if (!status) return
    const { studentId } = status
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
    await refetchDataForRow(studentId)
  }

  const handleEditStatus = async (status: StatusType) => {
    statusWip = {
      ...status,
    }
    isStatusEditorOpen = true
  }

  const handleStatusDone = async () => {
    const { studentId } = statusWip as StatusType
    statusWip = null
    isStatusEditorOpen = false
    await refetchDataForRow(studentId as string)
  }

  $effect(() => {
    if (group && statusCategory) {
      fetchData()
    }
  })
</script>

{#if group && statusCategory && subject}
  <h2 class="my-4">{group?.displayName} - {statusCategory?.title}</h2>
  <section class="shadow-sm">
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
          <span class="item header-row-item">Status</span>

          {#each students as student, rowIndex (student.id)}
            <span class="item student-name">
              <Link to="/students/{student.id}">
                {student.name}
              </Link>
            </span>
            <span class="item">
              {#each statusesByStudentId[student.id] as status, statusIndex (status.id)}
                {@const masterySchema = $dataStore.masterySchemas.find(
                  ms => ms.id === status.masterySchemaId
                )}
                {#if statusIndex > 0}
                  <hr class="status-divider" />
                {/if}
                <div class="status-entry">
                  <div class="status-card-header mb-2">
                    <span class="status-title">
                      {#if status.id}
                        <Link to="/statuses/{status.id}">
                          {status.title}
                        </Link>
                      {:else}
                        {status.title}
                      {/if}
                    </span>

                    {#if status.id}
                      <span class="status-meta">
                        <AuthorInfo item={status} />
                      </span>
                    {:else}
                      <span class="status-meta status-unsaved">Ikke lagret</span>
                    {/if}

                    <div class="status-card-actions">
                      {#if status.id && $hasUserAccessToFeature( 'status', 'update', { groupId, createdById: status.createdById, subjectId: subject.id, studentGroupIds: [group.id] } )}
                        <ButtonIcon
                          options={{
                            iconName: 'edit',
                            title: 'Rediger status',
                            classes: 'bordered',
                            onClick: () => handleEditStatus(status),
                          }}
                        />
                      {/if}

                      {#if status.id && $hasUserAccessToFeature( 'status', 'delete', { groupId, createdById: status.createdById, subjectId: subject.id, studentGroupIds: [group.id] } )}
                        <ButtonIcon
                          options={{
                            iconName: 'trash-can',
                            title: 'Slett status',
                            classes: 'bordered',
                            onClick: () => handleDeleteStatus(status),
                            delayActionFor: 2,
                          }}
                        />
                      {/if}
                    </div>
                  </div>
                  <div
                    onchange={() => handleChangeStatus(status, rowIndex)}
                    class="mastery-input-container"
                  >
                    <MasteryValueInput {masterySchema} bind:value={status.masteryValue} />
                  </div>
                  {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
                    <span class="fst-italic">
                      {status.masteryDescription}
                    </span>
                  {/if}
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
  </section>
{:else}
  <h2>Manglende data</h2>
  <p>Denne komponenten krever (foreløpig) at gruppa er knyttet til et fag</p>
  <p>Gruppe: {group?.id}</p>
  <p>Statuskategori: {statusCategory?.id}</p>
  <p>Fag: {subject?.id}</p>
{/if}

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit status={statusWip} onDone={handleStatusDone} />
  {/if}
</Offcanvas>

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
    align-items: stretch;
    justify-content: flex-start;
    gap: 0.5rem;
    border-bottom: 4px solid var(--bs-border-color);
  }

  .students-grid .item.header-row-item {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .students-grid .item:first-child,
  .students-grid .item.student-name {
    align-items: start;
  }

  .status-divider {
    margin: 0.1rem 0;
    border: 2px dotted var(--bs-border-color);
    opacity: 1;
  }

  .status-entry {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }

  .status-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    min-height: 32px; /* Same height as the edit/delete mini buttons */
  }

  .status-card-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex-shrink: 0;
    margin-left: auto;
  }

  .status-title {
    font-weight: 600;
    color: var(--bs-body-color);
  }

  .status-meta {
    font-size: 0.75rem;
    color: var(--bs-secondary-color, #6c757d);
  }

  .status-unsaved {
    font-style: italic;
  }

  .mastery-input-container {
    width: 100%;
    margin-bottom: 0.3rem;
  }
</style>
