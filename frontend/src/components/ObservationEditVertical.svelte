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
  const origLevels = $derived(masterySchema?.config?.levels || [])
  const masteryLevels = $derived(origLevels.reverse() || [])
  const minValue = $derived(
    masteryLevels.length ? masteryLevels[masteryLevels.length - 1].minValue : 1
  )
  const maxValue = $derived(masteryLevels.length ? masteryLevels[0].maxValue : 100)
  const sliderValueIncrement = $derived(masteryLevels.length ? masteryLevels[0].increment || 1 : 1)
  const widthMultiplier = $derived(masteryLevels.length ? 100 / masteryLevels.length : 1)

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
</script>

<div class="observation-edit p-4">
  <h3 class="pb-2">
    {localObservation.id ? 'Redigerer observasjon' : 'Ny observasjon'}
  </h3>

  <div class="mb-4">
    <label class="form-label" for="mastery-slider">
      Hvor ofte mestrer {student?.name}: {goal?.title}
    </label>

    <div class="d-flex gap-3 position-relative">
      <input
        id="mastery-slider"
        type="range"
        min={minValue}
        max={maxValue}
        step={sliderValueIncrement}
        class="slider"
        bind:value={localObservation.masteryValue}
      />

      {#if masterySchema?.config?.isIncrementIndicatorEnabled}
        <div
          id="incrementIndicator"
          style="top: calc(max(0px, {100 - localObservation.masteryValue}% - 3px));"
        ></div>
      {/if}

      <div class="stairs-container">
        {#each masteryLevels as masteryLevel, index}
          <span
            class="rung px-2"
            style="width: {(index + 1) *
              widthMultiplier}%; background-color: {(localObservation.masteryValue ?? 0) >=
            masteryLevel.minValue
              ? masteryLevel.color
              : 'var(--bs-gray)'};"
          >
            {masteryLevel.title}
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
  #incrementIndicator {
    position: absolute;
    top: 0;
    left: 10%;
    width: 90%;
    height: 5px;
    background-color: rgba(0, 0, 0, 0.25);
    z-index: 1;
  }

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
  }

  .slider {
    margin: 0px 20px 0px 20px;
    width: 10px;
    writing-mode: vertical-lr;
    direction: rtl;
    padding-top: 0px;
    background-color: var(--bs-gray);
    z-index: 2;
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
