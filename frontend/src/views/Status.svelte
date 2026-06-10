<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
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
  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'
  import ButtonMini from '../components/ButtonMini.svelte'
  import StatusEdit from '../components/StatusEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import AuthorInfo from '../components/AuthorInfo.svelte'
  import Link from '../components/Link.svelte'
  import MasterySchemaLevel from '../components/MasterySchemaLevel.svelte'

  let { statusId } = $props<{
    statusId: string
  }>()

  let status = $state<StatusType | null>(null)
  let statusWip = $state<Partial<StatusType> | null>(null)
  let student = $state<UserType | null>(null)
  let subject = $state<SubjectType | null>(null)
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

      if (status) {
        // Fetch student
        const studentResult = await usersRetrieve({ path: { id: status.studentId } })
        student = studentResult.data!
        if (status.subjectId) {
          // Fetch subject
          const subjectResult = await subjectsRetrieve({ path: { id: status.subjectId } })
          subject = subjectResult.data!
        }
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
    try {
      await statusDestroy({ path: { id: statusId } })
      trackEvent('Status', 'Delete')

      window.history.back() // Navigate back to whence it came!
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
  {:else if status && student}
    <!-- Header -->
    <div class="p-4 pb-3 border-bottom border-3 border-primary">
      <h2 class="fs-5 fw-semibold mb-0">
        {status.title} for
        <mark><Link to="/students/{student.id}">{student.name}</Link></mark>
        {#if subject}
          i faget
          <mark>{subject.shortName || subject.displayName}</mark>
        {/if}
      </h2>
      <p class="small text-muted mt-1 mb-0">
        {formatDateHumanly(status.beginAt) || '?'} – {formatDateHumanly(status.endAt) || '?'}
      </p>
    </div>

    <div class="p-4">
      <!-- Updated by info and action buttons -->
      <div class="field-group d-flex justify-content-between align-items-center">
        <div>
          <p class="text-muted mb-0">
            <AuthorInfo item={status} />
          </p>
        </div>
        <div class="d-flex gap-2">
          {#if $hasUserAccessToFeature( 'status', 'edit', { subjectId: subject?.id, studentGroupIds: student.groupIds } )}
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
          {/if}
          {#if $hasUserAccessToFeature( 'status', 'delete', { subjectId: subject?.id, studentGroupIds: student.groupIds } )}
            <ButtonMini
              options={{
                title: 'Slett status',
                skin: 'secondary',
                iconName: 'trash-can',
                variant: 'icon-left',
                classes: 'me-2',
                onClick: handleDelete,
                delayActionFor: 3,
              }}
            >
              Slett
            </ButtonMini>
          {/if}
        </div>
      </div>

      <!-- Kategori -->
      <div class="field-group">
        <span class="field-label">Kategori</span>
        <div>
          {#if status.categoryId}
            {$dataStore.statusCategories.find(cat => cat.id === status?.categoryId)?.title ||
              'ukjent'}
          {:else}
            ingen
          {/if}
        </div>
      </div>

      <!-- Periode -->
      <div class="field-group">
        <span class="field-label">Periode</span>
        <p class="mb-0">
          {formatDateHumanly(status.beginAt)} – {formatDateHumanly(status.endAt)}
        </p>
      </div>

      <!-- Mestring -->
      {#if masterySchema?.config?.isMasteryValueInputEnabled && status.masteryValue !== null && status.masteryValue !== undefined}
        <div class="field-group">
          <span class="field-label">Mestring</span>
          <div
            class="mastery-scale"
            class:mastery-scale-horizontal={masterySchema?.config?.valueInput ===
              'sliderHorizontal'}
            class:mastery-scale-vertical={masterySchema?.config?.valueInput === 'sliderVertical'}
          >
            {#each calculations.masteryLevels as level}
              <span
                class="mastery-level-wrapper"
                class:active={status.masteryValue >= level.minValue &&
                  status.masteryValue <= level.maxValue}
                class:inactive={status.masteryValue < level.minValue ||
                  status.masteryValue > level.maxValue}
              >
                <MasterySchemaLevel
                  masteryValue={level.minValue}
                  masterySchemaId={status.masterySchemaId}
                />
              </span>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Beskrivelse -->
      {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
        <div class="field-group">
          <span class="field-label">Beskrivelse</span>
          <div>
            {status.masteryDescription || 'ingen beskrivelse'}
          </div>
        </div>
      {/if}

      <!-- Fremovermelding -->
      {#if masterySchema?.config?.isFeedforwardInputEnabled}
        <div class="field-group">
          <span class="field-label">Fremovermelding</span>
          <div>
            {status.feedforward || 'ingen fremovermelding'}
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <p>Status ikke funnet</p>
  {/if}
</section>

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
  .field-group {
    padding: 1rem 0;
    border-bottom: 1px solid var(--pkt-color-grays-gray-100, #e6e6e6);
  }

  .field-group:last-child {
    border-bottom: none;
  }

  .field-label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
  }

  .field-group :not(.field-label) {
    font-size: 1.1rem;
  }

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

  .mastery-level-wrapper {
    transition: opacity 0.2s;
  }

  .mastery-level-wrapper.active {
    opacity: 1;
  }

  .mastery-level-wrapper.inactive {
    opacity: 0.2;
    filter: grayscale(30%);
  }
</style>
