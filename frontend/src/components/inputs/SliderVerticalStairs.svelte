<script lang="ts">
  import type { ObservationType } from '../../generated/types.gen'
  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import { getContrastFriendlyTextColor } from '../../utils/functions'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import ObservationMarkers from './ObservationMarkers.svelte'

  let {
    masterySchema,
    masteryValue = $bindable(),
    label = 'Mastery Value',
    isInputEnabled = true,
    observations = [],
  }: {
    masterySchema: MasterySchemaWithConfig
    masteryValue: number
    label?: string
    isInputEnabled?: boolean
    observations?: ObservationType[]
  } = $props()

  const thumbHeight = 50
  let inputContainerHeight = $state(0)

  const calculations = $derived(useMasteryCalculations(masterySchema))

  const calculateThumbCenter = (value: number) =>
    inputContainerHeight * (1 - calculations.calculateValuePosition(value) / 100)

  const thumbCenterY = $derived(calculateThumbCenter(masteryValue))

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

<div class="mb-2">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="d-flex gap-1 position-relative mt-4">
    {#if masterySchema?.config?.isMasteryValueInputEnabled && isInputEnabled}
      <!-- Slider input -->
      <input
        id="mastery-slider"
        type="range"
        min={calculations.minValue}
        max={calculations.maxValue}
        step={calculations.inputValueIncrement}
        class="slider"
        style="--track-height: {inputContainerHeight}px; --thumb-height: {thumbHeight}px; --thumb-overhang: {thumbHeight /
          2}px;"
        bind:value={masteryValue}
      />
    {/if}

    {#if masterySchema?.config?.isMasteryValueVisible}
      <!-- mastery value number -->
      <div id="value-indicator-container">
        <div id="value-indicator" style="top: {thumbCenterY}px;">
          {safeMasteryValue}
        </div>
      </div>
    {/if}

    <div class="stairs-container" bind:clientHeight={inputContainerHeight}>
      {#each sortedMasteryLevels as masteryLevel, index}
        <!-- levels -->
        <span
          class="rung px-2"
          style="width: {(index + 1) * widthMultiplier}%; height: {calculations.calculateRungWidth(
            calculations.masteryLevels.indexOf(masteryLevel)
          )}%; background-color: {masteryLevel.color}; color: {getContrastFriendlyTextColor(
            masteryLevel.color
          )};"
        >
          {masteryLevel.title}
        </span>
      {/each}
      {#if masterySchema?.config?.isIncrementIndicatorEnabled}
        <!-- bar visualizing mastery position -->
        <div
          id="increment-indicator"
          title={`${safeMasteryValue}`}
          style="top: {thumbCenterY}px;"
        ></div>
        <ObservationMarkers
          {observations}
          calculatePosition={calculateThumbCenter}
          orientation="horizontal"
        />
      {/if}
    </div>
  </div>
</div>

<style>
  #increment-indicator {
    position: absolute;
    top: 0;
    left: 0%;
    width: 100%;
    height: 4px;
    transform: translateY(-50%);
    background-color: rgba(0, 0, 0, 0.8);
    z-index: 1;
  }

  #value-indicator-container {
    position: relative;
    width: 3em;
  }

  #value-indicator {
    position: absolute;
    top: 0;
    left: 0;
    width: 3em;
    height: 1.5em;
    line-height: 1.5em;
    z-index: 2;
    text-align: center;
    transform: translateY(-50%);
  }

  .stairs-container {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-end;
    width: 100%;
    height: 200px;
  }

  .rung {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: medium;
  }

  .slider {
    margin: calc(0px - var(--thumb-overhang)) 20px;
    padding: 0;
    width: 10px;
    height: calc(var(--track-height) + var(--thumb-height));
    flex-shrink: 0;
    align-self: flex-start;
    z-index: 2;
    writing-mode: vertical-lr;
    direction: rtl;
    background: linear-gradient(
      to bottom,
      transparent var(--thumb-overhang),
      var(--bs-gray) var(--thumb-overhang),
      var(--bs-gray) calc(100% - var(--thumb-overhang)),
      transparent calc(100% - var(--thumb-overhang))
    );
    box-sizing: border-box;
    -webkit-appearance: none;
    appearance: none;
    outline: none;
  }

  .slider::-webkit-slider-runnable-track {
    width: 10px;
    height: 100%;
  }

  .slider::-moz-range-track {
    width: 10px;
    height: 100%;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 40px;
    height: var(--thumb-height);
    border-radius: 3px;
    box-sizing: border-box;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .slider::-moz-range-thumb {
    width: 40px;
    height: var(--thumb-height);
    border-radius: 3px;
    box-sizing: border-box;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
</style>
