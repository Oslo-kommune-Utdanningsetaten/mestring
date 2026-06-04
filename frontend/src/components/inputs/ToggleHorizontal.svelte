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

  // generate a unique name to ensure multiple instances of this component can coexist
  const inputName = `mastery-toggle-${Math.random().toString(36).slice(2)}`

  const calculations = $derived(useMasteryCalculations(masterySchema))
  const { masteryLevels } = $derived(calculations)
</script>

{#if label}
  <label class="form-label" for="mastery-slider">
    {label}
  </label>
{/if}
<div class="d-flex justify-content-center">
  <div class="radio-buttons">
    {#each masteryLevels as masteryLevel}
      <label class="radio" style="--particle-color: {masteryLevel.color}">
        <input
          type="radio"
          name={inputName}
          value={masteryLevel.minValue}
          bind:group={masteryValue}
          disabled={!isInputEnabled || !masterySchema?.config?.isMasteryValueInputEnabled}
        />
        <span class="name">{masteryLevel.title}</span>
      </label>
    {/each}
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
    box-sizing: border-box;
    width: 100%;
    font-size: 0.9rem;
    gap: 0.3rem;
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
    background-color: #ddd;
  }

  .radio-buttons .radio input:checked + .name {
    background-color: #fff;
    font-weight: 600;
  }

  /* Hover effect */
  .radio-buttons .radio:hover .name {
    box-shadow: 0 0 0px 1px rgba(0, 0, 0, 0.06);
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
