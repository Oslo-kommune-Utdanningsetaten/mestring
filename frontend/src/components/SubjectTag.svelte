<script lang="ts">
  import type { SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { getSubjectName } from '../utils/functions'
  import Link from './Link.svelte'

  const { subjectId, href, classes } = $props<{
    subjectId: string | null | undefined
    onclick?: () => void
    href?: string
    classes?: string
  }>()

  const skin: string = 'gray'
  const subject = $derived($dataStore.subjects.find((sub: SubjectType) => sub.id === subjectId))
  const subjectName = $derived(getSubjectName(subject))
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
</style>
