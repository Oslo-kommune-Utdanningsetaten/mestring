<script lang="ts">
  import { useMasteryCalculations, type MasterySchemaWithConfig } from '../utils/masteryHelpers'

  let {
    masterySchema,
    masteryValue = $bindable(),
    label = 'Mastery Value',
  }: {
    masterySchema: MasterySchemaWithConfig
    masteryValue: number
    label?: string
  } = $props()

  const calculations = $derived(useMasteryCalculations(masterySchema))
  let thumbXPosition = $derived(
    Math.round(
      ((masteryValue - calculations.minValue) / (calculations.maxValue - calculations.minValue)) *
        100
    )
  )
  let xOffset = $derived(thumbXPosition > 40 ? -((thumbXPosition - 40) / 40) * 1.1 : 0)

  const rungWidth = $derived(
    calculations.masteryLevels.length ? 100 / calculations.masteryLevels.length : 100
  )
  const safeMasteryValue = $derived(calculations.calculateSafeMasteryValue(masteryValue))

  const calculateRungHeight = (index: number) => {
    return (index + 1) * (100 / calculations.masteryLevels.length)
  }

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

  <div class="stairs-container d-flex align-items-end mb-3">
    {#each calculations.masteryLevels as masteryLevel, index}
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
        style="left: clamp(0%, {thumbXPosition + xOffset}%, calc(100% - 10px));"
      ></div>
    {/if}
  </div>

  <div class="input-container d-flex align-items-end my-5">
    <input
      id="mastery-slider"
      type="range"
      min={calculations.minValue}
      max={calculations.maxValue}
      step={calculations.sliderValueIncrement}
      class="slider"
      bind:value={masteryValue}
    />
    {#if masterySchema?.config?.isIncrementIndicatorEnabled}
      <div
        id="valueIndicator"
        style="left: clamp(0%, calc({thumbXPosition + xOffset}% - 0.5rem), calc(100%));"
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
    width: 10px;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.25);
  }

  #valueIndicator {
    position: absolute;
    bottom: 1.2em;
    left: 0;
    text-align: center;
    width: auto;
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
