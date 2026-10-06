<script lang="ts">
  import type { ObservationType } from '../../generated/types.gen'

  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import { getContrastFriendlyTextColor } from '../../utils/functions'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import ObservationMarkers from './ObservationMarkers.svelte'

  const arrowHeadWidth = 40

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

  const {
    minValue,
    maxValue,
    inputValueIncrement,
    masteryLevels,
    hasLevels,
    defaultValue,
    calculateValuePosition,
    calculateRungWidth,
    calculateSafeMasteryValue,
  } = $derived(useMasteryCalculations(masterySchema))

  const thumbWidth = 40
  let inputContainerWidth = $state(0)

  const calculateThumbCenter = (value: number) =>
    (inputContainerWidth * calculateValuePosition(value)) / 100

  const thumbXPosition = $derived(calculateValuePosition(masteryValue))
  const thumbCenterX = $derived(calculateThumbCenter(masteryValue))

  const safeMasteryValue = $derived(calculateSafeMasteryValue(masteryValue))

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

{#snippet incrementIndicatorShape(faded: boolean)}
  <div class="increment-indicator-shape" class:increment-indicator-faded={faded}>
    <div class="increment-indicator-bar"></div>
    <div class="increment-indicator-arrow"></div>
  </div>
{/snippet}

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
      style="width: {calculateRungWidth(index)}%;"
    >
      <span class="pb-1 mx-2 lh-sm" style="color: {getContrastFriendlyTextColor(rungColor)};">
        {masteryLevel.title}
      </span>
    </span>
  {/each}
  {#if masterySchema?.config?.isIncrementIndicatorEnabled}
    <!-- horizontal arrow visualizing mastery position -->
    <div
      id="increment-indicator"
      title={`${safeMasteryValue}`}
      style="--thumb-position: {thumbCenterX}px; --arrow-head-width: {arrowHeadWidth}px; --indicator-color: {rungColor};"
    >
      {@render incrementIndicatorShape(true)}
      <div class="increment-indicator-clip">
        {@render incrementIndicatorShape(false)}
      </div>
    </div>
    <ObservationMarkers {observations} calculatePosition={calculateThumbCenter} inset="0 -1px" />
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
      min={minValue}
      max={maxValue}
      step={inputValueIncrement}
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
    border: 1px solid var(--bs-gray);
  }

  .input-container {
    position: relative;
    height: 20px;
    width: 100%;
  }

  #increment-indicator {
    position: absolute;
    left: 0px;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    height: 40px;
    pointer-events: none;
  }

  .increment-indicator-shape {
    position: absolute;
    left: 0;
    top: 0;
    width: clamp(0px, var(--thumb-position), 100%);
    height: 40px;
  }

  .increment-indicator-clip {
    position: absolute;
    inset: 0;
    overflow: hidden;
  }

  .increment-indicator-faded {
    opacity: 0.5;
  }

  .increment-indicator-bar {
    position: absolute;
    left: 0;
    top: 10px;
    width: clamp(0px, calc(100% - var(--arrow-head-width)), 100%);
    height: 20px;
    background-color: var(--indicator-color);
  }

  .increment-indicator-arrow {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: var(--arrow-head-width) solid var(--indicator-color);
    border-top: 20px solid transparent;
    border-bottom: 20px solid transparent;
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
    height: 100%;
    background-color: white;
  }

  .rung span {
    font-size: 1.5rem;
    font-weight: 600;
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
    width: var(--thumb-width);
    height: 50px;
    border-radius: 3px;
    appearance: none;
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
