<script lang="ts">
  import { onMount } from 'svelte'
  import { formatISO } from 'date-fns'

  import { dataStore } from '../stores/data'
  import type {
    Student as StudentType,
    Observation as ObservationType,
    Goal as GoalType,
  } from '../types/models'

  const { student, goal, observation } = $props<{
    student: StudentType
    goal: GoalType
    observation: ObservationType | null
  }>()
  const masteryLevels = $derived($dataStore.masteryLevels)

  let slider: HTMLInputElement
  let masteryIndicator: HTMLElement
  let value = $state(observation ? observation.masteryValue : 50)
  let submitting = $state(false)
  let error = $state('')

  $effect(() => {
    if (masteryIndicator) {
      masteryIndicator.style.width = `${value}%`
    }
  })

  function handleSliderInput() {
    value = Number(slider.value)
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('nb-NO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  function saveObservation() {
    submitting = true
    error = ''

    try {
      const newObservationId = `obs-${student.id}-${Date.now()}`

      const newObservation: ObservationType = {
        id: newObservationId,
        createdAt: formatISO(new Date(), { format: 'extended' }),
        masteryValue: value,
        groupId: goal.groupId,
        goalId: goal.id,
        studentId: student.id,
      }

      // Add to the observations array in the dataStore
      dataStore.update(state => {
        // Add the new observation
        const observations = [...state.observations, newObservation]

        // Update the goal's observationIds array
        const goals = state.goals.map(g => {
          if (g.id === goal.id) {
            return {
              ...g,
              observationIds: [...g.observationIds, newObservationId],
            }
          }
          return g
        })

        return {
          ...state,
          observations,
          goals,
        }
      })
    } catch (err) {
      error = 'Kunne ikke lagre observasjon. Prøv igjen senere.'
      console.error('Error saving observation:', err)
    } finally {
      submitting = false
    }
  }

  onMount(() => {
    slider.value = value.toString()
  })
</script>

<div class="observation-edit">
  <h3>{observation ? 'Rediger observasjon' : 'Ny observasjon'}</h3>
  <p>Mål: {goal?.title || 'Ukjent mål'}</p>

  {#if error}
    <div class="alert alert-danger">{error}</div>
  {/if}

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
        bind:this={slider}
        on:input={handleSliderInput}
      />
    </div>
    <div id="slider-value" class="text-center">{value}%</div>
  </div>

  <div class="d-flex gap-2 justify-content-end mt-4">
    <button class="btn btn-secondary" on:click={saveObservation} disabled={submitting}>
      {submitting ? 'Lagrer...' : 'Lagre observasjon'}
    </button>
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
