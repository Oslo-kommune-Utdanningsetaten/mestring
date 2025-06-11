<script lang="ts">
  import { dataStore } from '../stores/data'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import type { ObservationReadable, GoalReadable, UserReadable } from '../generated/types.gen'

  const { student, goal, observation, onDone } = $props<{
    student: UserReadable | null
    goal: GoalReadable | null
    observation: ObservationReadable | null
    onDone: () => void
  }>()

  const masteryLevels = [
    {
      text: 'Mestrer',
      minValue: 81,
      maxValue: 100,
      color: 'rgb(160, 207, 106)',
    },
    {
      text: 'Mestrer ofte',
      minValue: 61,
      maxValue: 80,
      color: 'rgb(241, 249, 97)',
    },
    {
      text: 'Mestrer iblant',
      minValue: 41,
      maxValue: 60,
      color: 'rgb(86, 174, 232)',
    },
    {
      text: 'Mestrer sjelden',
      minValue: 21,
      maxValue: 40,
      color: 'rgb(159, 113, 202)',
    },
    {
      text: 'Mestrer ikke',
      minValue: 1,
      maxValue: 20,
      color: 'rgb(229, 50, 43)',
    },
  ]

  const levelMultiplier = 100 / masteryLevels.length

  let localObservation = $state<ObservationReadable>({
    ...observation,
    masteryValue: observation?.masteryValue || 50,
  })

  async function handleSave() {
    localObservation.studentId = student?.id
    localObservation.goalId = goal?.id
    localObservation.observerId = $dataStore.currentUser?.id
    localObservation.observedAt = new Date().toISOString()

    try {
      if (localObservation.id) {
        // Update existing Observation
        const result = await observationsUpdate({
          path: { id: localObservation.id },
          body: localObservation,
        })
        console.log('Observation updated:', result.data)
      } else {
        // Create new Observation
        const result = await observationsCreate({
          body: localObservation,
        })
        console.log('Observation created:', result.data)
      }
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving Observation:', error)
    }
  }
</script>

<div class="observation-edit p-4">
  <h3 class="pb-2">
    {localObservation.id ? 'Redigerer observasjon' : 'Ny observasjon'}
  </h3>

  <div class="mb-4">
    <label class="form-label" for="mastery-slider">
      Hvor ofte mestrer {student?.name}: {goal?.title}
    </label>

    <div class="d-flex gap-2 position-relative">
      <input
        id="mastery-slider"
        type="range"
        min="1"
        max="100"
        step="1"
        class="slider"
        bind:value={localObservation.masteryValue}
      />

      <div class="stairs-container">
        {#each masteryLevels as masteryLevel, index}
          <span
            class="rung"
            style="width: {(index + 1) *
              levelMultiplier}%; background-color: {localObservation?.masteryValue >=
            masteryLevel.minValue
              ? masteryLevel.color
              : 'var(--bs-gray)'};"
          >
            {masteryLevel.text}
          </span>
        {/each}
      </div>
    </div>
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
    >
      Lagre
    </pkt-button>

    <pkt-button
      size="medium"
      skin="secondary"
      type="button"
      variant="label-only"
      class="m-2"
      onclick={() => onDone()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onDone()
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
  .stairs-container {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-end;
    width: 100%;
  }

  .rung {
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: medium;
    font-weight: bold;
  }

  .slider {
    margin: 0px 20px 0px 20px;
    width: 10px;
    writing-mode: vertical-lr;
    direction: rtl;
    padding-top: 0px;
    background-color: var(--bs-gray);
    z-index: 1;
  }

  .slider::-webkit-slider-thumb,
  .slider::-moz-range-thumb {
    width: 50px;
    height: 10px;
    border-radius: 3px;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
  }
</style>
