<script lang="ts">
  import type { MasterySchemaType } from '../generated'
  import SliderVertical from './inputs/SliderVertical.svelte'
  import SliderHorizontal from './inputs/SliderHorizontal.svelte'
  import StarsHorizontal from './inputs/StarsHorizontal.svelte'
  import ToggleHorizontal from './inputs/ToggleHorizontal.svelte'
  import SliderGiraffe from './inputs/SliderGiraffe.svelte'
  import ToggleComicHorizontal from './inputs/ToggleComicHorizontal.svelte'
  import SliderArrowHorizontal from './inputs/SliderArrowHorizontal.svelte'

  let {
    masterySchema,
    value = $bindable(),
    title,
    isInputEnabled = true,
  } = $props<{
    masterySchema: MasterySchemaType
    value?: number
    title?: string
    isInputEnabled?: boolean
  }>()
</script>

{#if masterySchema?.config?.valueInput === 'sliderVertical'}
  <SliderVertical {masterySchema} {isInputEnabled} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'sliderHorizontal'}
  <SliderHorizontal
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === 'starsHorizontal'}
  <StarsHorizontal {masterySchema} {isInputEnabled} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'toggleHorizontal'}
  <ToggleHorizontal
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === 'sliderGiraffe'}
  <SliderGiraffe {masterySchema} {isInputEnabled} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === 'toggleComicHorizontal'}
  <ToggleComicHorizontal
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === 'sliderArrowHorizontal'}
  <SliderArrowHorizontal
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else}
  <p class="text-danger">
    Ugyldig masterySchema.config: {masterySchema?.config?.valueInput}
  </p>
{/if}

<style>
</style>
