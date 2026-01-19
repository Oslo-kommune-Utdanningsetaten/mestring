<script lang="ts">
  import type { StatusType, SubjectType, UserType, GoalType } from '../generated/types.gen'
  import {
    statusRetrieve,
    usersRetrieve,
    subjectsRetrieve,
    statusDestroy,
  } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import { formatDateHumanly } from '../utils/functions'
  import ButtonMini from '../components/ButtonMini.svelte'
  import StatusEdit from '../components/StatusEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import { addAlert } from '../stores/alerts'

  let { statusId } = $props<{
    statusId: string
  }>()

  let status = $state<StatusType | null>(null)
  let statusWip = $state<Partial<StatusType> | null>(null)
  let student = $state<UserType | null>(null)
  let subject = $state<SubjectType | null>(null)
  let updatedByUser = $state<UserType | null>(null)
  let isLoading = $state<boolean>(true)
  let isStatusEditorOpen = $state<boolean>(false)

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === status?.masterySchemaId) ||
      $dataStore.defaultMasterySchema
  )

  const calculations = $derived(useMasteryCalculations(masterySchema))

  const fetchData = async () => {
    isLoading = true
    try {
      // Fetch status
      const statusResult = await statusRetrieve({ path: { id: statusId } })
      status = statusResult.data!

      if (!status) {
        isLoading = false
        return
      }

      // Fetch student
      const studentResult = await usersRetrieve({ path: { id: status.studentId } })
      student = studentResult.data!

      // Fetch subject
      const subjectResult = await subjectsRetrieve({ path: { id: status.subjectId } })
      subject = subjectResult.data!

      // Fetch updatedBy user
      if (status.updatedById) {
        const updatedByResult = await usersRetrieve({ path: { id: status.updatedById } })
        updatedByUser = updatedByResult.data!
      }
    } catch (error) {
      console.error('Error fetching status data:', error)
    } finally {
      isLoading = false
    }
  }

  const handleEditStatus = async () => {
    statusWip = {
      ...status,
    }
    isStatusEditorOpen = true
  }

  const handleStatusDone = async () => {
    isStatusEditorOpen = false
    statusWip = null
    await fetchData()
  }

  const handleDelete = async () => {
    if (!status) return
    const confirmMessage = `Er du sikker på at du vil slette status "${status.title}"?`
    if (!window.confirm(confirmMessage)) return
    try {
      await statusDestroy({ path: { id: statusId } })

      window.history.back() // Navigate back to whence it came!
      addAlert({
        type: 'success',
        message: `Slettet status "${status.title}"`,
      })
    } catch (error) {
      console.error('Error deleting status:', error)
      addAlert({
        type: 'warning',
        message: `Kunne ikke slette status "${status.title}". Hvis du tror dette er en feil, kontakt support.`,
      })
    }
  }

  $effect(() => {
    if (statusId) {
      fetchData()
    }
  })
</script>

<section>
  {#if isLoading}
    <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Laster...</span>
      </div>
    </div>
  {:else if status && subject && student}
    <!-- Name and subject -->
    <h2 class="my-3">
      Status for
      <mark>{student.name}</mark>
      i faget
      <mark>{subject.shortName || subject.displayName}</mark>
      , {status.title}
    </h2>

    <!-- Updated by info and action buttons -->
    <div class="d-flex justify-content-between align-items-center my-3">
      <div>
        {#if updatedByUser}
          <p class="text-muted mb-0">
            Sist endret av {updatedByUser.name}, {formatDateHumanly(status.updatedAt)}
          </p>
        {/if}
      </div>
      <div class="d-flex gap-2">
        <ButtonMini
          options={{
            title: 'Rediger status',
            skin: 'secondary',
            iconName: 'edit',
            variant: 'icon-left',
            classes: 'me-2',
            onClick: handleEditStatus,
          }}
        >
          Rediger
        </ButtonMini>
        <ButtonMini
          options={{
            title: 'Slett status',
            skin: 'secondary',
            iconName: 'trash-can',
            variant: 'icon-left',
            classes: 'me-2',
            onClick: handleDelete,
          }}
        >
          Slett
        </ButtonMini>
      </div>
    </div>

    <hr />

    <!-- Begin and end dates -->
    <div class="row my-4">
      <h3 class="col-4">Periode</h3>
      <div class="col-8">
        <p class="mb-0">
          {formatDateHumanly(status.beginAt)} – {formatDateHumanly(status.endAt)}
        </p>
      </div>
    </div>

    <hr />

    <!-- Mastery value display -->
    {#if masterySchema?.config?.isMasteryValueInputEnabled && status.masteryValue !== null && status.masteryValue !== undefined}
      <div class="row my-4">
        <h3 class="col-4">Mestring</h3>
        <div class="col-8">
          <div
            class="mastery-scale"
            class:mastery-scale-horizontal={masterySchema?.config?.renderDirection === 'horizontal'}
            class:mastery-scale-vertical={masterySchema?.config?.renderDirection === 'vertical'}
          >
            {#each calculations.masteryLevels as level}
              <div
                class="mastery-level"
                class:active={status.masteryValue >= level.minValue &&
                  status.masteryValue <= level.maxValue}
                class:inactive={status.masteryValue < level.minValue ||
                  status.masteryValue > level.maxValue}
                style="--level-color: {level.color}; background-color: var(--level-color);"
              >
                <strong>{level.title}</strong>
              </div>
            {/each}
          </div>
          <p class="mt-2">
            {status.masteryValue}
          </p>
        </div>
      </div>
    {/if}

    <!-- Mastery description display -->
    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="row my-4">
        <h3 class="col-4">Beskrivelse</h3>
        <div class="col-8">
          {status.masteryDescription || 'ingen beskrivelse'}
        </div>
      </div>
    {/if}

    <!-- Mastery feed forward display -->
    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="row my-4">
        <h3 class="col-4">Fremovermelding</h3>
        <div class="col-8">
          {status.feedforward || 'ingen fremovermelding'}
        </div>
      </div>
    {/if}
  {:else}
    <p>Status ikke funnet</p>
  {/if}
</section>

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  width="80vw"
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit status={statusWip} {subject} onDone={handleStatusDone} />
  {/if}
</Offcanvas>

<style>
  .mastery-scale {
    display: flex;
    gap: 0.5rem;
  }

  .mastery-scale-vertical {
    flex-direction: column;
  }

  .mastery-scale-horizontal {
    flex-direction: row;
  }

  .mastery-level {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
  }

  .mastery-scale-horizontal .mastery-level {
    flex: 1;
    text-align: center;
  }

  .mastery-level.active {
    border-color: color-mix(in srgb, var(--level-color) 70%, rgba(0, 0, 0, 0.7));
    border-width: 5px;
    border-style: outset;
    font-weight: 600;
  }

  .mastery-level.inactive {
    filter: grayscale(30%);
    opacity: 0.4;
  }
</style>
