<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { statusRetrieve, usersRetrieve, subjectsRetrieve } from '../generated/sdk.gen'

  import { dataStore } from '../stores/data'
  import { formatDateHumanly } from '../utils/functions'

  import MasterySchemaLevels from '../components/MasterySchemaLevels.svelte'
  import AuthorInfo from '../components/AuthorInfo.svelte'
  import Link from '../components/Link.svelte'
  import StatusWidgets from '../components/edit/StatusWidgets.svelte'

  let { statusId } = $props<{
    statusId: string
  }>()

  let status = $state<StatusType | undefined>(undefined)
  let student = $state<UserType | undefined>(undefined)
  let subject = $state<SubjectType | undefined>(undefined)
  let isLoading = $state<boolean>(true)

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === status?.masterySchemaId) ||
      $dataStore.defaultMasterySchema
  )

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
          <StatusWidgets
            {status}
            {student}
            {subject}
            onRefreshRequired={() => fetchData()}
            widgets={['update', 'delete']}
            buttonSize="large"
          />
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
            <span class="text-muted">ingen</span>
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
      <div class="field-group">
        <span class="field-label">Mestring</span>
        <MasterySchemaLevels masteryValue={status.masteryValue} {masterySchema} />
      </div>

      <!-- Beskrivelse -->
      {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
        <div class="field-group">
          <span class="field-label">Beskrivelse</span>
          <div>
            {#if status.masteryDescription}
              {status.masteryDescription}
            {:else}
              <span class="text-muted">ingen beskrivelse</span>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Fremovermelding -->
      {#if masterySchema?.config?.isFeedforwardInputEnabled}
        <div class="field-group">
          <span class="field-label">Fremovermelding</span>
          <div>
            {#if status.feedforward}
              {status.feedforward}
            {:else}
              <span class="text-muted">ingen fremovermelding</span>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <p>Status ikke funnet</p>
  {/if}
</section>

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
</style>
