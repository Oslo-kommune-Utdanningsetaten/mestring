<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { ObservationType } from '../generated/types.gen'

  import { currentSchool } from '../stores/data'
  import InvisibleSVG from '../assets/eye-visible.svg.svelte'
  import VisibleSVG from '../assets/eye-invisible.svg.svelte'

  const { observation } = $props<{
    observation: ObservationType
  }>()
</script>

{#if $currentSchool.isServiceEnabledForStudents}
  {#if observation.isVisibleToStudent}
    <span class="svg" title="Synlig for eleven" aria-hidden="true">
      <VisibleSVG />
    </span>
  {:else}
    <span class="svg" title="Ikke synlig for eleven" aria-hidden="true">
      <InvisibleSVG />
    </span>
  {/if}
{/if}

<style>
  .svg > :global(svg) {
    height: 1.4rem;
    padding-bottom: 0.1rem;
    padding-left: 0.1rem;
    padding-right: 0.1rem;
  }
</style>
