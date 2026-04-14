<script lang="ts">
  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import Giraffe from './Giraffe.svelte'

  let {
    masterySchema,
    masteryValue = $bindable(),
    label = 'Mastery Value',
    isInputEnabled = true,
  }: {
    masterySchema: MasterySchemaWithConfig
    masteryValue: number
    label?: string
    isInputEnabled?: boolean
  } = $props()

  const calculations = $derived(useMasteryCalculations(masterySchema))
  let thumbYPosition = $state(0)
  let yOffset = $state(0)

  const safeMasteryValue = $derived(calculations.calculateSafeMasteryValue(masteryValue))

  // Set default value when masteryValue is null/undefined and schema is available
  $effect(() => {
    if ((masteryValue === null || masteryValue === undefined) && calculations.hasLevels) {
      masteryValue = calculations.defaultValue
    }
  })

  $effect(() => {
    const min = Number(calculations.minValue ?? 0)
    const max = Number(calculations.maxValue ?? 100)
    thumbYPosition = Math.round(((masteryValue - min) / (max - min)) * 100)
    yOffset = -Math.round((thumbYPosition / 100) * 5)
  })
</script>

<div class="mb-4">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="d-flex gap-1 position-relative">
    {#if masterySchema?.config?.isMasteryValueInputEnabled && isInputEnabled}
      <input
        id="mastery-slider"
        type="range"
        min={calculations.minValue}
        max={calculations.maxValue}
        step={calculations.sliderValueIncrement}
        class="slider"
        bind:value={masteryValue}
      />
      {#if masterySchema?.config?.isValueIndicatorEnabled && isInputEnabled}
        <div id="valueIndicatorContainer">
          <div
            id="valueIndicator"
            style="bottom: clamp(0%, calc({thumbYPosition +
              yOffset}% - 0.75em), calc(100% - 1.5em));"
          >
            {safeMasteryValue}
          </div>
        </div>
      {/if}
    {/if}

    <div class="giraffe-container">
      <Giraffe min={calculations.minValue} max={calculations.maxValue} value={masteryValue} />
    </div>
  </div>
</div>

<style>
  #valueIndicatorContainer {
    position: relative;
    width: 3em;
    border: 1px solid var(--bs-gray-300);
  }

  #valueIndicator {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 3em;
    height: 1.5em;
    line-height: 1.5em;
    z-index: 2;
    text-align: center;
    transition: left 0.2s ease-out;
  }

  .slider {
    margin: 0px 20px 0px 20px;
    padding-top: 0px;
    padding-bottom: 0px;
    width: 10px;
    z-index: 2;
    writing-mode: vertical-lr;
    direction: rtl;
    background-color: var(--bs-gray);
    -webkit-appearance: none;
    appearance: none;
    outline: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 40px;
    height: 50px;
    border-radius: 3px;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .slider::-moz-range-thumb {
    width: 40px;
    height: 50px;
    border-radius: 3px;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
</style>
