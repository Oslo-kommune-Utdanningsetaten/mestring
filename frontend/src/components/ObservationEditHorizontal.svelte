<script lang="ts">
  import { dataStore } from '../stores/data'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import type { ObservationReadable, GoalReadable, UserReadable } from '../generated/types.gen'

  const { student, goal, observation, onDone } = $props<{
    student: UserReadable | null
    goal: GoalReadable | null
    observation: ObservationReadable | {} | null
    onDone: () => void
  }>()

  const masterySchema = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
  )
  const masteryLevels = $derived(masterySchema?.schema?.levels || [])
  const minValue = $derived(masteryLevels.length ? masteryLevels[0].minValue : 1)
  const maxValue = $derived(
    masteryLevels.length ? masteryLevels[masteryLevels.length - 1].maxValue : 100
  )
  const sliderValueIncrement = $derived(masteryLevels.length ? masteryLevels[0].increment || 1 : 1)
  const rungWidth = $derived(masteryLevels.length ? 100 / masteryLevels.length : 100)

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
        const result = await observationsUpdate({
          path: { id: localObservation.id },
          body: localObservation,
        })
      } else {
        const result = await observationsCreate({
          body: localObservation,
        })
      }
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving Observation:', error)
    }
  }

  const calculateRungHeight = (index: number) => {
    const result = (index + 1) * (100 / masteryLevels.length)
    console.log(`Rung height for index ${index}: ${result}%`)
    return result
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

    <div class="stairs-container d-flex align-items-end mb-3">
      {#each masteryLevels as masteryLevel, index}
        <span
          class="rung flex-grow d-flex align-items-end justify-content-center text-center"
          style="width: {rungWidth}%; height: {calculateRungHeight(
            index
          )}%; background-color: {(localObservation.masteryValue ?? 0) >= masteryLevel.minValue
            ? masteryLevel.color
            : 'var(--bs-gray)'};"
        >
          <span class="pb-2 mx-2">
            {masteryLevel.title}
          </span>
        </span>
      {/each}
      {#if masterySchema?.schema?.isIncrementIndicatorEnabled}
        <div
          id="incrementIndicator"
          style="left: calc(max(0px, {localObservation.masteryValue}% - 5px));"
        ></div>
      {/if}
    </div>

    <input
      id="mastery-slider"
      type="range"
      min={minValue}
      max={maxValue}
      step={sliderValueIncrement}
      class="slider"
      bind:value={localObservation.masteryValue}
    />
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
    height: 200px;
    width: 100%;
  }

  #incrementIndicator {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.25);
  }

  .rung {
    font-size: medium;
  }

  .slider {
    width: 100%;
    height: 5px;
    padding-top: 0px;
    background-color: var(--bs-gray);
  }

  .slider::-webkit-slider-thumb,
  .slider::-moz-range-thumb {
    width: 5px;
    height: 30px;
    border-radius: 3px;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
  }
</style>
