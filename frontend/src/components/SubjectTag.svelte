<script lang="ts">
  import type { SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'

  const { subjectId } = $props<{
    subjectId: string | null | undefined
  }>()

  const subject = $derived($dataStore.subjects.find((sub: SubjectType) => sub.id === subjectId))
</script>

<span class="subject">
  {#if subject}
    {subject.shortName || subject.displayName || subject.grepCode || `Fag med id ${subject.id}`}
  {:else}
    ukjent fag :/
  {/if}
</span>

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
