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
  const sortedMasteryLevels: MasteryConfigLevel[] = $derived(
    [...masteryLevels].sort((a, b) => b.minValue - a.minValue)
  )
  const minValue = $derived(
    Math.min(...masteryLevels.map((lev: MasteryConfigLevel) => lev.minValue))
  )
  const maxValue = $derived(
    Math.max(...masteryLevels.map((lev: MasteryConfigLevel) => lev.maxValue))
  )
  const sliderValueIncrement = $derived(masterySchema?.config?.inputIncrement || 1)
  const widthMultiplier = $derived(masteryLevels.length ? 100 / masteryLevels.length : 1)

  $effect(() => {
    if (!isNumber(masteryValue)) {
      masteryValue = minValue + maxValue / 2
    }
  })
</script>

<div class="mb-4">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="d-flex gap-3 position-relative">
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
        id="incrementIndicator"
        style="top: calc(max(0px, {100 - (masteryValue ?? 0)}% - 3px));"
      ></div>
    {/if}

    <div class="stairs-container">
      {#each sortedMasteryLevels as masteryLevel, index}
        <span
          class="rung px-2"
          style="width: {(index + 1) * widthMultiplier}%; background-color: {(masteryValue ?? 0) >=
          masteryLevel.minValue
            ? masteryLevel.color
            : 'var(--bs-gray)'};"
        >
          {masteryLevel.title}
        </span>
      {/each}
    </div>
  </div>
</div>

<style>
  #incrementIndicator {
    position: absolute;
    top: 0;
    left: 10%;
    width: 90%;
    height: 5px;
    background-color: rgba(0, 0, 0, 0.25);
    z-index: 1;
    transition: top 0.2s ease-out;
  }

  .stairs-container {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-end;
    width: 100%;
  }

  .rung {
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: medium;
  }

  .slider {
    margin: 0px 20px 0px 20px;
    width: 10px;
    writing-mode: vertical-lr;
    direction: rtl;
    padding-top: 0px;
    background-color: var(--bs-gray);
    z-index: 2;
  }

  .slider::-webkit-slider-thumb,
  .slider::-moz-range-thumb {
    width: 50px;
    height: 10px;
    border-radius: 3px;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
  }
</style>
