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
    <pkt-icon
      class="watermark-icon pkt-icon--large"
      name="achievement"
      aria-hidden="true"
    ></pkt-icon>
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
    justify-content: center;
    min-height: 32px;
    padding: 0.25rem 0.5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    overflow: hidden;
    gap: 0.125rem;
  }

  .watermark-icon {
    position: absolute;
    top: 50%;
    left: -0.5rem;
    transform: translateY(-50%);
    opacity: 0.15;
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
