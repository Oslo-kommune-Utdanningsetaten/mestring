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

  const calculations = $derived(useMasteryCalculations(masterySchema))
  const { masteryLevels } = $derived(calculations)
  const values = $derived(masteryLevels.map((level: any) => level.minValue))

  let hoveredValue = $state<number | null>(null)

  const isValueHighlighted = (value: number): boolean => {
    const targetValue = hoveredValue ?? masteryValue
    return targetValue !== null && value <= targetValue
  }

  // Get the color for a specific star value from its corresponding mastery level
  const getStarColor = (value: number): string => {
    const level = masteryLevels.find((ml: any) => ml.minValue === value)
    return level?.color || '#ff9e0b' // fallback color
  }

  const handleStarClick = (value: number) => {
    if (isInputEnabled) {
      masteryValue = value
    }
  }

  // Set default value when masteryValue is null/undefined and schema is available
  $effect(() => {
    if ((masteryValue === null || masteryValue === undefined) && calculations.hasLevels) {
      masteryValue = calculations.defaultValue
    }
  })
</script>

<div class="mt-4 mb-4">
  <label class="form-label" for="mastery-slider">
    {label}
  </label>

  <div class="radio">
    {#each values as value, index}
      <label
        for="rating-{value}"
        title="{value} stjerne{value > 1 ? 'r' : ''}"
        class:highlighted={isValueHighlighted(value)}
        style="--star-color: {getStarColor(value)}"
        onmouseenter={() => (hoveredValue = value)}
        onmouseleave={() => (hoveredValue = null)}
        onclick={() => handleStarClick(value)}
      >
        <input
          id="rating-{value}"
          type="radio"
          name="mastery-stars"
          bind:value={masteryValue}
          checked={masteryValue === value}
          disabled={!isInputEnabled}
        />
        <svg viewBox="0 0 576 512" height="2em" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"
          ></path>
        </svg>
      </label>
    {/each}
  </div>
</div>

<style>
  .form-label {
    font-weight: 600;
  }

  .radio {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 2rem 0rem 3rem 0rem;
  }

  .radio input {
    position: absolute;
    appearance: none;
  }

  .radio label {
    cursor: pointer;
    font-size: 30px;
    position: relative;
    display: inline-block;
    transition: transform 0.3s ease;
  }

  .radio label svg {
    fill: #666;
    transition: fill 0.3s ease;
  }

  .radio label::before,
  .radio label::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    background-color: var(--star-color);
    border-radius: 50%;
    opacity: 0;
    transform: scale(0);
    transition:
      transform 0.4s ease,
      opacity 0.4s ease;
  }

  .radio label::before {
    top: -15px;
    left: 50%;
    transform: translateX(-50%) scale(0);
  }

  .radio label::after {
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%) scale(0);
  }

  .radio label:hover::before,
  .radio label:hover::after {
    opacity: 1;
    transform: translateX(-50%) scale(1.5);
  }

  .radio label:hover {
    transform: scale(1.2);
    animation: pulse 0.6s infinite alternate;
  }

  /* Apply highlighted styles when star should be filled */
  .radio label.highlighted svg {
    fill: var(--star-color);
    filter: drop-shadow(0 0 15px var(--star-color));
    animation: shimmer 1s ease infinite alternate;
  }

  /* Extra emphasis on hover */
  .radio label:hover.highlighted svg {
    animation: pulse 0.8s infinite alternate;
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    100% {
      transform: scale(1.1);
    }
  }

  @keyframes shimmer {
    0% {
      filter: drop-shadow(0 0 10px color-mix(in srgb, var(--star-color) 50%, transparent));
    }
    100% {
      filter: drop-shadow(0 0 20px var(--star-color));
    }
  }
</style>
