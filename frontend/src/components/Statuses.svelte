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
      statuses = (result.data || []).sort(
        (a, b) => new Date(a.beginAt).getTime() - new Date(b.beginAt).getTime()
      )
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
      <span class="status-item" title={status.title}>
        <Link to={`/statuses/${status.id}/`}>{status.title}</Link>
      </span>
    {/each}
  </div>
{/if}

<style>
  .statuses-container {
    position: relative;
    display: flex;
    flex-direction: column;
    min-height: 32px;
    padding: 0.25rem 0.5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    overflow: hidden;
    gap: 0.125rem;
  }

  /* Watermark using pseudo-element */
  .statuses-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: -10% center;
    background-size: 80px;
    opacity: 0.1;
    pointer-events: none;
    z-index: 0;
  }

  .status-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    line-height: 1.2;
    z-index: 1;
  }
</style>
