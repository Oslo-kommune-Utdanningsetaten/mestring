<script lang="ts">
  import type { ObservationType, MasterySchemaType } from '../generated/types.gen'

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
    observations = [],
  } = $props<{
    masterySchema: MasterySchemaType
    value?: number | undefined | null
    title?: string
    isInputEnabled?: boolean
    observations?: ObservationType[]
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
    {observations}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else}
  <div class="text-danger">
    <h3>Huhmf, ugyldig masterySchema</h3>
    <pre>
      {JSON.stringify(masterySchema, null, 2)}
    </pre>
  </div>
{/if}

<style></style>
