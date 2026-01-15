<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
  import { statusList } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'

  let { student, subject } = $props<{
    student: UserType
    subject: SubjectType
  }>()

  let statuses = $state<StatusType[]>([])
  let isLoading = $state(true)

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
    <pkt-icon name="achievement" size="small"></pkt-icon>
    {#each statuses as status (status.id)}
      <div class="status-item" title={status.title}>
        <Link to={`/statuses/${status.id}/`}>{status.title}</Link>
      </div>
    {/each}
  </div>
{/if}

<style>
  .statuses-container {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border-radius: 4px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
  }

  .status-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
