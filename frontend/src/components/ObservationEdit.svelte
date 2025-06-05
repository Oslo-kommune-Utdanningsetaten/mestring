<script lang="ts">
  import { onMount } from 'svelte'
  import type { ObservationReadable, GoalReadable, UserReadable } from '../api/types.gen'

  const { student, goal, observation, onSave, onCancel } = $props<{
    student: UserReadable | null
    goal: GoalReadable | null
    observation: ObservationReadable | null
    onSave: (observation: any) => void
    onCancel: () => void
  }>()

  const masteryLevels = [
    {
      text: 'Mestrer ikke',
    },
    {
      text: 'Mestrer sjelden',
    },
    {
      text: 'Mestrer iblant',
    },
    {
      text: 'Mestrer ofte',
    },
    {
      text: 'Mestrer',
    },
  ]

  let sliderInput: HTMLInputElement
  let masteryIndicator: HTMLElement
  let localObservation = $state<Record<string, any>>({ ...observation })
  let value = $state(localObservation.masteryValue || 50)

  function handleSliderInput() {
    value = Number(sliderInput.value)
  }

  const handleSave = () => {
    localObservation.studentId = student?.id
    localObservation.goalId = goal?.id
    localObservation.masteryValue = value
    onSave(localObservation)
  }

  $effect(() => {
    if (masteryIndicator) {
      masteryIndicator.style.width = `${value}%`
    }
  })

  $effect(() => {
    if (localObservation) {
      localObservation.masteryValue = value
    }
  })
</script>

<div class="observation-edit p-4">
  <h3 class="pb-2">
    {localObservation.id ? 'Redigerer observasjon for' : 'Ny observasjon for'}
    {student?.name}
  </h3>
  <p>Mål: {goal?.title}</p>

  <div class="mb-4">
    <label class="form-label">Mestringsnivå</label>
    <div class="stairs-container">
      {#each masteryLevels as masteryLevel}
        <span class="rung">{masteryLevel.text}</span>
      {/each}
      <div id="slider-value-indicator" bind:this={masteryIndicator}></div>
    </div>
    <div class="slider-container mb-2">
      <input
        type="range"
        min="1"
        max="100"
        {value}
        class="slider"
        bind:this={sliderInput}
        oninput={() => handleSliderInput()}
      />
    </div>
    <div id="slider-value" class="text-center">{value}%</div>
  </div>

  <div class="d-flex gap-2 justify-content-start mt-4">
    <pkt-button
      size="medium"
      skin="primary"
      type="button"
      variant="label-only"
      class="m-2"
      onclick={() => handleSave()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleSave()
        }
      }}
      role="button"
      tabindex="0"
      disabled={false}
    >
      Lagre
    </pkt-button>

    <pkt-button
      size="medium"
      skin="secondary"
      type="button"
      variant="label-only"
      class="m-2"
      onclick={() => onCancel()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onCancel()
        }
      }}
      role="button"
      tabindex="0"
    >
      Avbryt
    </pkt-button>
  </div>
</div>

<style>
  :root {
    --color-1: rgb(229, 50, 43);
    --color-2: rgb(159, 113, 202);
    --color-3: rgb(86, 174, 232);
    --color-4: rgb(241, 249, 97);
    --color-5: rgb(160, 207, 106);
    --slider-thumb-color: #04aa6d;
    --slider-track-color: #d3d3d3;
  }

  #slider-value-indicator {
    position: absolute;
    top: 0;
    left: 0;
    padding: 5px 10px;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.4);
    backdrop-filter: saturate(250%);
    transition: width 0.2s ease-out;
  }

  .stairs-container {
    position: relative;
    display: flex;
    justify-content: space-evenly;
    align-items: flex-end;
    margin-bottom: 20px;
  }

  .rung {
    width: 20%;
    border-top-left-radius: 5px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    padding-bottom: 5px;
    font-size: small;
    font-weight: bold;
  }

  .stairs-container > span:nth-child(1) {
    height: 30px;
    background-color: var(--color-1);
  }
  .stairs-container > span:nth-child(2) {
    height: 70px;
    background-color: var(--color-2);
  }
  .stairs-container > span:nth-child(3) {
    height: 100px;
    background-color: var(--color-3);
  }
  .stairs-container > span:nth-child(4) {
    height: 150px;
    background-color: var(--color-4);
  }
  .stairs-container > span:nth-child(5) {
    height: 190px;
    background-color: var(--color-5);
  }

  .slider {
    -webkit-appearance: none;
    width: 100%;
    height: 15px;
    background: var(--slider-track-color);
    outline: none;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .slider::-webkit-slider-thumb,
  .slider::-moz-range-thumb {
    width: 15px;
    height: 25px;
    border-radius: 6px;
    background: var(--slider-thumb-color);
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
  }
</style>
