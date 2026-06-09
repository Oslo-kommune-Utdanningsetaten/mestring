<script lang="ts">
  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import { getContrastFriendlyTextColor } from '../../utils/functions'
  import type { MasterySchemaWithConfig } from '../../types/models'

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

  const {
    minValue,
    maxValue,
    inputValueIncrement,
    masteryLevels,
    hasLevels,
    defaultValue,
    calculateSafeMasteryValue,
  } = $derived(useMasteryCalculations(masterySchema))

  let thumbXPosition = $derived(
    Math.round(((masteryValue - minValue) / (maxValue - minValue)) * 100)
  )
  let xOffset = $derived(thumbXPosition > 40 ? -((thumbXPosition - 40) / 40) * 1.1 : 0)

  const safeMasteryValue = $derived(calculateSafeMasteryValue(masteryValue))

  const calculateRungWidth = (index: number) => {
    const currentLevel = masteryLevels[index]
    const valuesCountTotal = maxValue - minValue + 1
    const valuesCountCurrentLevel = currentLevel.maxValue - currentLevel.minValue + 1
    return (valuesCountCurrentLevel / valuesCountTotal) * 100
  }

  const parseColor = (color: string) => {
    const rgb = color.match(/rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/)
    if (rgb) return { r: parseInt(rgb[1]), g: parseInt(rgb[2]), b: parseInt(rgb[3]), a: 1 }
    const rgba = color.match(/rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)/)
    if (rgba)
      return {
        r: parseInt(rgba[1]),
        g: parseInt(rgba[2]),
        b: parseInt(rgba[3]),
        a: parseFloat(rgba[4]),
      }
    const hex = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})?$/i.exec(color)
    return hex
      ? {
          r: parseInt(hex[1], 16),
          g: parseInt(hex[2], 16),
          b: parseInt(hex[3], 16),
          a: hex[4] !== undefined ? parseInt(hex[4], 16) / 255 : 1,
        }
      : { r: 0, g: 0, b: 0, a: 1 }
  }

  const interpolateColor = (color1: string, color2: string, t: number) => {
    const c1 = parseColor(color1)
    const c2 = parseColor(color2)
    const r = Math.round(c1.r + (c2.r - c1.r) * t)
    const g = Math.round(c1.g + (c2.g - c1.g) * t)
    const b = Math.round(c1.b + (c2.b - c1.b) * t)
    const a = c1.a + (c2.a - c1.a) * t
    return a < 1 ? `rgba(${r}, ${g}, ${b}, ${a.toFixed(3)})` : `rgb(${r}, ${g}, ${b})`
  }

  const rungColor = $derived(
    masteryLevels.length > 1
      ? interpolateColor(
          masteryLevels[0].color,
          masteryLevels[masteryLevels.length - 1].color,
          thumbXPosition / 100
        )
      : (masteryLevels[0]?.color ?? '#cccccc')
  )

  // Set default value when masteryValue is null/undefined and schema is available
  $effect(() => {
    if ((masteryValue === null || masteryValue === undefined) && hasLevels) {
      masteryValue = defaultValue
    }
  })
</script>

{#if label}
  <label class="form-label" for="mastery-slider">
    {label}
  </label>
{/if}

<div class="stairs-container d-flex align-items-end">
  {#each masteryLevels as masteryLevel, index}
    <span
      class="rung flex-grow d-flex align-items-end {index === 0
        ? 'justify-content-start text-start'
        : index === masteryLevels.length - 1
          ? 'justify-content-end text-end'
          : 'justify-content-center text-center'}"
      style="width: {calculateRungWidth(index)}%; height:100%; background-color: {rungColor};"
    >
      <span class="pb-1 mx-2 lh-sm" style="color: {getContrastFriendlyTextColor(rungColor)};">
        {masteryLevel.title}
      </span>
    </span>
  {/each}
  {#if masterySchema?.config?.isIncrementIndicatorEnabled}
    <!-- horizontal arrow visualizing mastery position -->
    <div
      id="incrementIndicator"
      title={`${safeMasteryValue}`}
      style="width: clamp(0px, calc({thumbXPosition}% - 40px), calc(100%));"
    ></div>
  {/if}
</div>

<div
  class="input-container d-flex align-items-end mt-{masterySchema?.config?.isValueIndicatorEnabled
    ? '5'
    : '3'} mb-4"
>
  {#if masterySchema?.config?.isValueIndicatorEnabled}
    <!-- mastery value number -->
    <div
      id="valueIndicator"
      style="left: clamp(0%, calc({thumbXPosition + xOffset}% - 0.5rem), calc(100%));"
    >
      {safeMasteryValue}
    </div>
  {/if}
  {#if masterySchema?.config?.isMasteryValueInputEnabled && isInputEnabled}
    <!-- slider input -->
    <input
      id="mastery-slider"
      type="range"
      min={minValue}
      max={maxValue}
      step={inputValueIncrement}
      class="slider"
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
    border: 1px solid var(--bs-gray);
  }

  .input-container {
    position: relative;
    height: 20px;
    width: 100%;
  }

  #incrementIndicator {
    position: absolute;
    left: 0px;
    top: 50%;
    transform: translateY(-50%);
    height: 20px;
    background-color: rgba(0, 0, 0, 0.4);
    pointer-events: none;
  }

  #incrementIndicator::after {
    content: '';
    position: absolute;
    right: -40px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 40px solid rgba(0, 0, 0, 0.4);
    border-top: 20px solid transparent;
    border-bottom: 20px solid transparent;
  }

  #valueIndicator {
    position: absolute;
    bottom: 2em;
    left: 0;
    text-align: center;
    width: auto;
  }

  .rung {
    font-size: medium;
  }

  .rung span {
    font-size: 1.5rem;
    font-weight: 600;
  }

  .slider {
    width: 100%;
    height: 10px;
    padding-top: 0px;
    background-color: var(--bs-gray);
    -webkit-appearance: none;
    appearance: none;
    outline: none;
  }

  .slider::-webkit-slider-thumb {
    /* Override default look */
    -webkit-appearance: none;
    appearance: none;
    width: 50px;
    height: 40px;
    border-radius: 3px;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .slider::-moz-range-thumb {
    width: 50px;
    height: 40px;
    border-radius: 3px;
    border: 1px solid var(--pkt-color-grays-gray-500);
    cursor: pointer;
    background-color: var(--pkt-color-grays-gray-100);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
</style>
