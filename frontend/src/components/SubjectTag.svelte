<script lang="ts">
  import type { SubjectType } from '../generated/types.gen'
  import Link from './Link.svelte'
  import { dataStore } from '../stores/data'

  const { subjectId } = $props<{
    subjectId: string | null | undefined
  }>()

  const subject = $derived($dataStore.subjects.find((sub: SubjectType) => sub.id === subjectId))
</script>

{#if subject}
  <span title={subject.id} class="subject">
    {subject.shortName || subject.displayName || subject.grepCode || 'Ukjent fag'}
  </span>
{:else}
  ukjent fag :/
{/if}

<style>
  .subject {
    align-self: flex-start;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #666;
    background: #ebebeb;
    padding: 0.1rem 0.4rem;
  }
</style>
