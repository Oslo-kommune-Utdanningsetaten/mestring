<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
  import { statusList } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { formatDate } from '../utils/functions'

  let { student, subject } = $props<{
    student: UserType
    subject: SubjectType
  }>()

  let statuses = $state<StatusType[]>([])
  let isLoading = $state(true)

  const generateTitle = (status: StatusType): string => {
    const beginDate = formatDate(status.beginAt)
    const endDate = formatDate(status.endAt)
    return `${beginDate} - ${endDate}`
  }

  const fetchStatuses = async () => {
    try {
      isLoading = true
      const result = await statusList({
        query: {
          students: student.id,
          subject: subject.id,
          school: $dataStore.currentSchool?.id,
        },
      })
      statuses = result.data || []
    } catch (error) {
      console.error('Error fetching statuses:', error)
    } finally {
      isLoading = false
    }
  }

  $effect(() => {
    if (student.id && subject.id && $dataStore.currentSchool?.id) {
      fetchStatuses()
    }
  })
</script>

{#if isLoading}
  <div class="spinner-border spinner-border-sm text-primary" role="status">
    <span class="visually-hidden">Laster...</span>
  </div>
{:else if statuses.length > 0}
  <div class="statuses-container">
    {#each statuses as status (status.id)}
      <div class="status-item" title={status.title}>
        <pkt-icon name="achievement" size="small"></pkt-icon>
        <span class="status-title">{status.title}</span>
      </div>
    {/each}
  </div>
{:else}
  <p class="text-muted fst-italic mb-0">Ingen statuser</p>
{/if}

<style>
  .statuses-container {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .status-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
