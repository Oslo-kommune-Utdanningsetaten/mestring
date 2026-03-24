<script lang="ts">
  import type { MasterySchemaType } from '../generated'
  import SliderVertical from './inputs/SliderVertical.svelte'
  import SliderHorizontal from './inputs/SliderHorizontal.svelte'
  import StarsHorizontal from './inputs/StarsHorizontal.svelte'
  import ToggleHorizontal from './inputs/ToggleHorizontal.svelte'
  import SliderGiraffe from './inputs/SliderGiraffe.svelte'
  import ToggleComicHorizontal from './inputs/ToggleComicHorizontal.svelte'

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

{#if masterySchema?.config?.valueInput === 'sliderVertical'}
  <SliderVertical {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'sliderHorizontal'}
  <SliderHorizontal {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'starsHorizontal'}
  <StarsHorizontal {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'toggleHorizontal'}
  <ToggleHorizontal {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'sliderGiraffe'}
  <SliderGiraffe {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'toggleComicHorizontal'}
  <ToggleComicHorizontal {masterySchema} bind:masteryValue={value} label={title || ''} />
{:else}
  <p class="text-danger">
    Ugyldig masterySchema.config: {masterySchema?.config?.valueInput}
  </p>
{/if}

<style>
</style>
