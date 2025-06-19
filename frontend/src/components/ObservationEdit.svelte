<script lang="ts">
  import { dataStore } from '../stores/data'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'
  import type {
    ObservationReadable,
    GoalReadable,
    UserReadable,
    MasterySchemaReadable,
  } from '../generated/types.gen'
  import type { GoalDecorated, MasterySchemaConfig } from '../types/models'

  type MasterySchemaWithConfig = MasterySchemaReadable & {
    config?: MasterySchemaConfig
  }

  const { student, goal, observation, onDone } = $props<{
    student: UserReadable | null
    goal: GoalReadable | null
    observation: ObservationReadable | {} | null
    onDone: () => void
  }>()

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
  )

  let localObservation = $state<ObservationReadable>({
    ...observation,
    masteryValue: observation?.masteryValue || 50,
  })

  function handleValueChange(newValue: number) {
    localObservation.masteryValue = newValue
  }

  const renderDirection = (goal: GoalDecorated): 'horizontal' | 'vertical' => {
    if (!goal || !$dataStore.masterySchemas) return 'vertical'
    const masterySchema = $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
    return masterySchema.config?.renderDirection === 'horizontal' ? 'horizontal' : 'vertical'
  }

  const handleSave = async () => {
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
    {#if renderDirection(goal) === 'vertical'}
      <ValueInputVertical
        {masterySchema}
        masteryValue={localObservation.masteryValue ?? 50}
        label="Hvor ofte mestrer {student?.name}: {goal?.title}"
        onValueChange={handleValueChange}
      />
    {:else}
      <ValueInputHorizontal
        {masterySchema}
        masteryValue={localObservation.masteryValue ?? 50}
        label="Hvor ofte mestrer {student?.name}: {goal?.title}"
        onValueChange={handleValueChange}
      />
    {/if}
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
</style>
