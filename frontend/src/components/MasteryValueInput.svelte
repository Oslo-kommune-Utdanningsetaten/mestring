<script lang="ts">
  import type { MasterySchemaType } from '../generated'
  import SliderInputVertical from './inputs/SliderInputVertical.svelte'
  import SliderInputHorizontal from './inputs/SliderInputHorizontal.svelte'

  let {
    masterySchema,
    value = $bindable(),
    title,
  } = $props<{
    masterySchema: MasterySchemaType
    value?: number
    title?: string
  }>()
</script>

<div class="mb-4">
  {#if masterySchema?.config?.valueInput === 'sliderVertical'}
    <SliderInputVertical {masterySchema} bind:masteryValue={value} label={title || ''} />
  {:else if masterySchema?.config?.valueInput === 'sliderHorizontal'}
    <SliderInputHorizontal {masterySchema} bind:masteryValue={value} label={title || ''} />
  {/if}
</div>
