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

  const calculations = $derived(useMasteryCalculations(masterySchema))
  const thumbWidth = 40
  let inputContainerWidth = $state(0)

  const calculateThumbCenter = (value: number) =>
    (inputContainerWidth * calculations.calculateValuePosition(value)) / 100

  const thumbCenterX = $derived(calculateThumbCenter(masteryValue))

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

{#if label}
  <label class="form-label" for="mastery-slider">
    {label}
  </label>
{/if}

<div class="stairs-container d-flex align-items-end mb-2">
  {#each calculations.masteryLevels as masteryLevel, index}
    <!-- levels -->
    <span
      class="rung flex-grow d-flex align-items-end justify-content-center text-center"
      style="width: {calculations.calculateRungWidth(index)}%; height: {calculateRungHeight(
        index
      )}%; background-color: {masteryLevel.color}; color: {getContrastFriendlyTextColor(
        masteryLevel.color
      )};"
    >
      <span class="pb-1 mx-2 lh-sm">
        {masteryLevel.title}
      </span>
    </span>
  {/each}

  {#if masterySchema?.config?.isIncrementIndicatorEnabled}
    <!-- bar visualizing mastery position -->
    <div
      id="increment-indicator"
      title={`${safeMasteryValue}`}
      style="left: {thumbCenterX}px;"
    ></div>
    <ObservationMarkers {observations} calculatePosition={calculateThumbCenter} />
  {/if}
</div>

<div
  class="input-container d-flex align-items-end mt-{masterySchema?.config?.isMasteryValueVisible
    ? '5'
    : '3'} mb-4"
  bind:clientWidth={inputContainerWidth}
>
  {#if masterySchema?.config?.isMasteryValueVisible}
    <!-- mastery value number -->
    <div id="value-indicator" style="left: {thumbCenterX}px;">
      {safeMasteryValue}
    </div>
  {/if}

  {#if masterySchema?.config?.isMasteryValueInputEnabled && isInputEnabled}
    <!-- slider input -->
    <input
      id="mastery-slider"
      type="range"
      min={calculations.minValue}
      max={calculations.maxValue}
      step={calculations.inputValueIncrement}
      class="slider"
      style="--thumb-width: {thumbWidth}px; --thumb-overhang: {thumbWidth / 2}px;"
      bind:value={masteryValue}
    />
  {/if}
</div>

<style>
  label {
    font-weight: 600;
  }

  .stairs-container {
    position: relative;
    height: 200px;
    width: 100%;
  }

  .input-container {
    position: relative;
    height: 20px;
    width: 100%;
  }

  #increment-indicator {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 4px;
    height: 100%;
    transform: translateX(-50%);
    background: repeating-linear-gradient(45deg, #00000044 0px 5px, #ffffff44 5px 10px);
  }

  #value-indicator {
    position: absolute;
    bottom: 2em;
    left: 0;
    text-align: center;
    width: auto;
    transform: translateX(-50%);
  }

  .rung {
    font-size: medium;
  }

  .slider {
    width: calc(100% + var(--thumb-width));
    margin-left: calc(0px - var(--thumb-overhang));
    flex-shrink: 0;
    height: 10px;
    padding: 0;
    background: linear-gradient(
      to right,
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
    width: 100%;
    height: 10px;
  }

  .slider::-moz-range-track {
    width: 100%;
    height: 10px;
  }

  .slider::-webkit-slider-thumb {
    /* Override default look */
    -webkit-appearance: none;
    appearance: none;
    width: var(--thumb-width);
    height: 50px;
    border-radius: 3px;
    box-sizing: border-box;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .slider::-moz-range-thumb {
    width: var(--thumb-width);
    height: 50px;
    border-radius: 3px;
    box-sizing: border-box;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
</style>
