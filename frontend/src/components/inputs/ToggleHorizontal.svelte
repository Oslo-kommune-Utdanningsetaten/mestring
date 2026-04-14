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

  <div class="d-flex justify-content-center">
    <div class="radio-buttons">
      {#each masteryLevels as masteryLevel}
        <label class="radio" style="--particle-color: {masteryLevel.color}">
          <input
            type="radio"
            name="radio"
            value={masteryLevel.minValue}
            bind:group={masteryValue}
            disabled={!isInputEnabled || !masterySchema?.config?.isMasteryValueInputEnabled}
          />
          <span class="name">{masteryLevel.title}</span>
        </label>
      {/each}
    </div>
  </div>
</div>

<style>
  .form-label {
    font-weight: 600;
  }

  .radio-buttons {
    position: relative;
    display: flex;
    flex-wrap: wrap;
    border-radius: 0.5rem;
    background-color: #eee;
    box-sizing: border-box;
    box-shadow: 0 0 0px 1px rgba(0, 0, 0, 0.06);
    min-width: 70%;
    font-size: 14px;
    margin: 2rem 0rem 1rem 0rem;
  }

  .radio-buttons .radio {
    flex: 1 1 auto;
    text-align: center;
  }

  .radio-buttons .radio input {
    display: none;
  }

  .radio-buttons .radio .name {
    display: flex;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    border-radius: 0.5rem;
    border: none;
    padding: 0.5rem 0;
    color: rgba(51, 65, 85, 1);
    transition: all 0.15s ease-in-out;
  }

  .radio-buttons .radio input:checked + .name {
    background-color: #fff;
    font-weight: 600;
  }

  /* Hover effect */
  .radio-buttons .radio:hover .name {
    background-color: rgba(255, 255, 255, 0.5);
  }

  /* Animation */
  .radio-buttons .radio input:checked + .name {
    position: relative;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    animation: select 0.3s ease;
  }

  @keyframes select {
    0% {
      transform: scale(0.95);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }

  /* Particles */
  .radio-buttons .radio input:checked + .name::before,
  .radio-buttons .radio input:checked + .name::after {
    content: '';
    position: absolute;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: var(--particle-color);
    opacity: 0;
    animation: particles 0.5s ease forwards;
  }

  .radio-buttons .radio input:checked + .name::before {
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
  }

  .radio-buttons .radio input:checked + .name::after {
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
  }

  @keyframes particles {
    0% {
      opacity: 0;
      transform: translateX(-50%) translateY(0);
    }
    50% {
      opacity: 1;
    }
    100% {
      opacity: 0;
      transform: translateX(-50%) translateY(var(--direction));
    }
  }

  .radio-buttons .radio input:checked + .name::before {
    --direction: -10px;
  }

  .radio-buttons .radio input:checked + .name::after {
    --direction: 10px;
  }
</style>
