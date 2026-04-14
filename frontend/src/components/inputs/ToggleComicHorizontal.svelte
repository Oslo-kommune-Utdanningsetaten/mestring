<script lang="ts">
  import { useMasteryCalculations } from '../../utils/masteryHelpers'
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

  const handleClick = (value: number) => {
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

  const groupId = Math.random().toString(36).slice(2, 8)
  const selectedIndex = $derived(
    masteryLevels.findIndex((level: any) => level.minValue === masteryValue)
  )
  const selectedColor = $derived(masteryLevels[Math.max(0, selectedIndex)]?.color ?? '#ffd700')
</script>

<div class="mt-4 mb-4">
  <label class="form-label">
    {label}
  </label>

  <div
    class="comic-radio-group"
    style="--option-count: {masteryLevels.length}; --selected-index: {selectedIndex}; --selected-color: {selectedColor}"
  >
    {#each masteryLevels as level, i}
      <input
        type="radio"
        name="mastery-{groupId}"
        id="mastery-{groupId}-{i}"
        value={level.minValue}
        bind:group={masteryValue}
        disabled={!isInputEnabled || !masterySchema?.config?.isMasteryValueInputEnabled}
      />
      <label for="mastery-{groupId}-{i}">
        {level.title}
      </label>
    {/each}
    <div class="comic-glider"></div>
  </div>
</div>

<style>
  .form-label {
    font-weight: 600;
  }

  .comic-radio-group {
    display: flex;
    position: relative;
    background: #ffd700;
    border-radius: 12px;
    border: 4px solid #000;
    box-shadow: 8px 8px 0px #000;
    overflow: hidden;
    width: fit-content;
    min-width: 70%;
    font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
    font-style: italic;
    font-weight: 500;
    margin: 2rem auto 1rem auto;
  }

  .comic-radio-group input {
    display: none;
  }

  .comic-radio-group label {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 80px;
    font-size: 20px;
    padding: 0.8rem 1.4rem;
    cursor: pointer;
    letter-spacing: 1px;
    color: #000;
    position: relative;
    z-index: 2;
    transition: color 0.3s ease-in-out;
    white-space: nowrap;
    text-shadow:
      -1px -1px 0 #fff,
      1px -1px 0 #fff,
      -1px 1px 0 #fff,
      1px 1px 0 #fff;
    box-shadow: inset 0 0 1px rgba(0, 0, 0, 0.5);
    border-radius: 8px;
  }

  .comic-radio-group input:checked + label {
    color: #fff;
    text-shadow:
      -2px -2px 0 #000,
      2px -2px 0 #000,
      -2px 2px 0 #000,
      2px 2px 0 #000;
  }

  .comic-radio-group input:disabled + label {
    cursor: default;
    opacity: 0.7;
  }

  .comic-glider {
    position: absolute;
    top: 0;
    bottom: 0;
    width: calc(100% / var(--option-count));
    border-radius: 8px;
    z-index: 1;
    transform: translateX(calc(var(--selected-index) * 100%));
    background-color: var(--selected-color);
    background-image: radial-gradient(circle at 4px 4px, rgba(0, 0, 0, 0.2) 2px, transparent 0);
    background-size: 8px 8px;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
    border-right: 4px solid #000;
    border-left: 4px solid #000;
    transition:
      transform 0.5s cubic-bezier(0.37, 1.95, 0.66, 0.56),
      background-color 0.4s ease-in-out,
      box-shadow 0.4s ease-in-out;
  }
</style>
