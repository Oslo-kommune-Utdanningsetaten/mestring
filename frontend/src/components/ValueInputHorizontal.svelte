<script lang="ts">
  import type { MasteryConfigLevel, MasterySchemaConfig } from '../types/models'
  import type { MasterySchemaReadable } from '../generated/types.gen'
  import { isNumber } from '../utils/functions'

  type MasterySchemaWithConfig = MasterySchemaReadable & {
    config?: MasterySchemaConfig
  }

  let {
    masterySchema,
    masteryValue = $bindable(),
    label = 'Mastery Value',
  }: {
    masterySchema: MasterySchemaWithConfig | null
    masteryValue?: number | null
    label?: string
  } = $props()

  const masteryLevels: MasteryConfigLevel[] = $derived(masterySchema?.config?.levels || [])
  const minValue = $derived(masteryLevels.length ? masteryLevels[0].minValue : 1)
  const maxValue = $derived(
    masteryLevels.length ? masteryLevels[masteryLevels.length - 1].maxValue : 100
  )
  const sliderValueIncrement = $derived(masterySchema?.config?.inputIncrement || 1)
  const rungWidth = $derived(masteryLevels.length ? 100 / masteryLevels.length : 100)
  // Always have a non-null numeric value available for rendering calculations
  const safeMasteryValue = $derived(
    isNumber(masteryValue) ? (masteryValue as number) : (minValue + maxValue) / 2
  )

  const calculateRungHeight = (index: number) => {
    return (index + 1) * (100 / masteryLevels.length)
  }
</script>

<div class="mb-4">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="stairs-container d-flex align-items-end mb-3">
    {#each masteryLevels as masteryLevel, index}
      <span
        class="rung flex-grow d-flex align-items-end justify-content-center text-center"
        style="width: {rungWidth}%; height: {calculateRungHeight(
          index
        )}%; background-color: {masteryLevel.color};"
      >
        <span class="pb-2 mx-2">
          {masteryLevel.title}
        </span>
      </span>
    {/each}
    {#if masterySchema?.config?.isIncrementIndicatorEnabled}
      <div
        id="incrementIndicator"
        style="left: calc(max(0px, {safeMasteryValue}% - {safeMasteryValue / 20}px));"
      ></div>
    {/if}
  </div>

  <div class="input-container d-flex align-items-end my-5">
    <input
      id="mastery-slider"
      type="range"
      min={minValue}
      max={maxValue}
      step={sliderValueIncrement}
      class="slider"
      bind:value={masteryValue}
    />
    {#if masterySchema?.config?.isIncrementIndicatorEnabled}
      <div
        id="valueIndicator"
        style="left: calc(max(0px, {safeMasteryValue}% - {safeMasteryValue / 10 + 5}px));"
      >
        {safeMasteryValue}
      </div>
    {/if}
  </div>
</div>

<style>
  .stairs-container {
    position: relative;
    height: 200px;
    width: 100%;
  }

  .input-container {
    position: relative;
    width: 100%;
  }

  #incrementIndicator {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.25);
    transition: left 0.2s ease-out;
  }

  #valueIndicator {
    position: absolute;
    bottom: 1.2em;
    left: 0;
    text-align: center;
    transition: left 0.2s ease-out;
  }

  .rung {
    font-size: medium;
  }

  .slider {
    width: 100%;
    height: 5px;
    padding-top: 0px;
    background-color: var(--bs-gray);
  }

  .slider::-webkit-slider-thumb,
  .slider::-moz-range-thumb {
    width: 5px;
    height: 30px;
    border-radius: 3px;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
  }
</style>
