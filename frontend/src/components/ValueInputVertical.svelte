<script lang="ts">
  import { useMasteryCalculations, type MasterySchemaWithConfig } from '../utils/masteryHelpers'

  let {
    masterySchema,
    masteryValue = $bindable(),
    label = 'Mastery Value',
  }: {
    masterySchema: MasterySchemaWithConfig | null
    masteryValue?: number | null
    label?: string
  } = $props()

  const calculations = $derived(useMasteryCalculations(masterySchema))
  const sortedMasteryLevels = $derived(
    [...calculations.masteryLevels].sort((a, b) => b.minValue - a.minValue)
  )
  const widthMultiplier = $derived(
    calculations.masteryLevels.length ? 100 / calculations.masteryLevels.length : 1
  )
  const safeMasteryValue = $derived(calculations.calculateSafeMasteryValue(masteryValue))

  // Set default value when masteryValue is null/undefined and schema is available
  $effect(() => {
    if ((masteryValue === null || masteryValue === undefined) && calculations.hasLevels) {
      masteryValue = calculations.defaultValue
    }
  })
</script>

<div class="mb-4">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="d-flex gap-1 position-relative">
    <input
      id="mastery-slider"
      type="range"
      min={calculations.minValue}
      max={calculations.maxValue}
      step={calculations.sliderValueIncrement}
      class="slider"
      bind:value={masteryValue}
    />
    <div id="valueIndicatorContainer">
      <div
        id="valueIndicator"
        style="top: clamp(0px, calc(100% - {safeMasteryValue}% - 0.75em), calc(100% - 1.3em));"
      >
        {safeMasteryValue}
      </div>
    </div>

    <div class="stairs-container">
      {#if masterySchema?.config?.isIncrementIndicatorEnabled}
        <div
          id="incrementIndicator"
          style="top: clamp(0px, calc(100% - {safeMasteryValue}%), calc(100% - 5px));"
        ></div>
      {/if}
      {#each sortedMasteryLevels as masteryLevel, index}
        <span
          class="rung px-2"
          style="width: {(index + 1) * widthMultiplier}%; background-color: {masteryLevel.color};"
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
    left: 0%;
    width: 100%;
    height: 5px;
    background-color: rgba(0, 0, 0, 0.25);
    z-index: 1;
    transition: top 0.2s ease-out;
  }

  #valueIndicatorContainer {
    width: 3em;
    border: 1px solid var(--bs-gray-300);
  }

  #valueIndicator {
    position: absolute;
    top: 0;
    left: 50px;
    width: 3em;
    height: 1.5em;
    line-height: 1.5em;
    z-index: 2;
    text-align: center;
    transition: left 0.2s ease-out;
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
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: medium;
  }

  .slider {
    margin: 0px 20px 0px 20px;
    padding-top: 0px;
    padding-bottom: 0px;
    width: 10px;
    writing-mode: vertical-lr;
    direction: rtl;
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
