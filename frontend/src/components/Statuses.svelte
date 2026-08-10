<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
  import { statusList } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { getPreferredCreatedParams } from '../utils/functions'
  import Link from './Link.svelte'

  let { student, subject } = $props<{
    student: UserType
    subject: SubjectType | null
  }>()

  let statuses = $state<StatusType[]>([])
  let isLoading = $state(true)

  const fetchStatuses = async () => {
    isLoading = true
    try {
      const query = {
        students: student.id,
        subject: subject ? subject.id : '',
        school: $dataStore.currentSchool?.id,
        ...getPreferredCreatedParams(),
      }
      const result = await statusList({ query })
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
    if (student.id && $dataStore.currentSchool?.id) {
      fetchStatuses()
    }
  })
</script>

{#if isLoading}
  <div class="spinner-border spinner-border-sm text-primary" role="status">
    <span class="visually-hidden">Laster...</span>
  </div>
{:else if statuses.length > 0}
  <ul class="statuses-container">
    <pkt-icon
      class="watermark-icon pkt-icon--large"
      name="achievement"
      aria-hidden="true"
    ></pkt-icon>

    {#each statuses as status (status.id)}
      <li class="status-item" title={status.title}>
        <Link to={`/statuses/${status.id}/`}>{status.title}</Link>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .statuses-container {
    position: relative;
    padding: 0.5rem 1.2rem;
    background: linear-gradient(
      to bottom,
      transparent,
      var(--pkt-color-surface-strong-light-green) 10%,
      var(--pkt-color-surface-strong-light-green) 90%,
      transparent
    );
    overflow: hidden;
    margin: 0;
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
    font-size: 0.75rem;
    line-height: 1.3;
    z-index: 1;
  }
</style>
