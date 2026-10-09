<script lang="ts">
  import type { ObservationType, MasterySchemaType } from '../generated/types.gen'
  import { VALUE_INPUT_VARIANT } from '../utils/constants'

  import SliderGiraffe from './inputs/SliderGiraffe.svelte'
  import SliderVertical from './inputs/SliderVertical.svelte'
  import SliderVerticalStairs from './inputs/SliderVerticalStairs.svelte'
  import SliderHorizontal from './inputs/SliderHorizontal.svelte'
  import SliderHorizontalArrow from './inputs/SliderHorizontalArrow.svelte'
  import SliderHorizontalStairs from './inputs/SliderHorizontalStairs.svelte'
  import StarsHorizontal from './inputs/StarsHorizontal.svelte'
  import ToggleHorizontal from './inputs/ToggleHorizontal.svelte'
  import ToggleHorizontalComic from './inputs/ToggleHorizontalComic.svelte'

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

{#if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_VERTICAL}
  <SliderVertical
    {masterySchema}
    {isInputEnabled}
    {observations}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_VERTICAL_STAIRS}
  <SliderVerticalStairs
    {masterySchema}
    {isInputEnabled}
    {observations}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_HORIZONTAL}
  <SliderHorizontal
    {masterySchema}
    {isInputEnabled}
    {observations}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_HORIZONTAL_STAIRS}
  <SliderHorizontalStairs
    {masterySchema}
    {isInputEnabled}
    {observations}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.STARS_HORIZONTAL}
  <StarsHorizontal {masterySchema} {isInputEnabled} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.TOGGLE_HORIZONTAL}
  <ToggleHorizontal
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_GIRAFFE}
  <SliderGiraffe {masterySchema} {isInputEnabled} bind:masteryValue={value} label={title || ''} />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.TOGGLE_HORIZONTAL_COMIC}
  <ToggleHorizontalComic
    {masterySchema}
    {isInputEnabled}
    bind:masteryValue={value}
    label={title || ''}
  />
{:else if masterySchema?.config?.valueInput === VALUE_INPUT_VARIANT.SLIDER_HORIZONTAL_ARROW}
  <SliderHorizontalArrow
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
