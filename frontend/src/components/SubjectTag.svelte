<script lang="ts">
  import type { SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'

  const { subjectId, title, onclick, href, classes } = $props<{
    subjectId: string | null | undefined
    onclick?: () => void
    href?: string
    classes?: string
  }>()

  const skin: string = 'gray'

  const subject = $derived($dataStore.subjects.find((sub: SubjectType) => sub.id === subjectId))
  const subjectName = $derived(
    subject ? subject.shortName || subject.displayName || subject.grep : 'ukjent fag'
  )
</script>

{#if href}
  <pkt-tag {skin} class={classes}>
    <Link to={href}>
      {subjectName}
    </Link>
  </pkt-tag>
{:else}
  <pkt-tag {skin} class={classes}>
    {subjectName}
  </pkt-tag>
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
