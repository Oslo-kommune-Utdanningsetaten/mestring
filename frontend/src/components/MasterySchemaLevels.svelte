<script lang="ts">
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import MasterySchemaLevel from './MasterySchemaLevel.svelte'

  let { masteryValue, masterySchema } = $props<{
    masteryValue?: number | null | undefined
    masterySchema: MasterySchemaWithConfig
  }>()

  const calculations = $derived(useMasteryCalculations(masterySchema))
  const isMasteryValueDefined = $derived(masteryValue != null) // Check if masteryValue is not null or undefined
</script>

{#if masterySchema?.config?.isMasteryValueInputEnabled}
  <div
    class="mastery-scale"
    class:mastery-scale-horizontal={masterySchema?.config?.valueInput === 'sliderHorizontal'}
    class:mastery-scale-vertical={masterySchema?.config?.valueInput === 'sliderVertical'}
  >
    {#each calculations.masteryLevels as level}
      <span
        class="mastery-level-wrapper"
        class:active={!isMasteryValueDefined ||
          (masteryValue >= level.minValue && masteryValue <= level.maxValue)}
        class:inactive={isMasteryValueDefined &&
          (masteryValue < level.minValue || masteryValue > level.maxValue)}
      >
        <MasterySchemaLevel masteryValue={level.minValue} masterySchemaId={masterySchema.id} />
      </span>
    {/each}
  </div>
{/if}

<style>
  .mastery-scale {
    display: flex;
    gap: 0.5rem;
  }

  .mastery-scale-vertical {
    flex-direction: column;
  }

  .mastery-scale-horizontal {
    flex-direction: row;
  }

  .mastery-level-wrapper {
    transition: opacity 0.2s;
  }

  .mastery-level-wrapper.active {
    opacity: 1;
  }

  .mastery-level-wrapper.inactive {
    opacity: 0.2;
    filter: grayscale(30%);
  }
</style>
