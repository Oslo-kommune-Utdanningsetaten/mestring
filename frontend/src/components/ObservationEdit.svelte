<script lang="ts">
  import { dataStore } from '../stores/data'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'
  import type { ObservationReadable, GoalReadable, UserReadable } from '../generated/types.gen'
  import type { GoalDecorated, MasterySchemaWithConfig } from '../types/models'

  const { student, goal, observation, onDone } = $props<{
    student: UserReadable | null
    goal: GoalReadable | null
    observation: ObservationReadable | {} | null
    onDone: () => void
  }>()

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
  )

  let localObservation = $state<Partial<ObservationReadable>>({
    masteryValue: null,
  })

  // Update localObservation when observation prop changes
  $effect(() => {
    if (observation) {
      localObservation = {
        ...observation,
        masteryValue: observation?.masteryValue,
      }
    } else {
      localObservation = {
        masteryValue: null,
      }
    }
  })

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
          body: localObservation as any,
        })
      } else {
        const result = await observationsCreate({
          body: localObservation as any,
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
    {localObservation.id ? 'Redigerer' : 'Ny'} observasjon
  </h3>

  {#if masterySchema?.config?.isMasteryValueInputEnabled}
    <div class="mb-4">
      {#if renderDirection(goal) === 'vertical'}
        <ValueInputVertical
          {masterySchema}
          bind:masteryValue={localObservation.masteryValue}
          label="Hvor ofte mestrer {student?.name}: {goal?.title}"
        />
      {:else}
        <ValueInputHorizontal
          {masterySchema}
          bind:masteryValue={localObservation.masteryValue}
          label="Hvor ofte mestrer {student?.name}: {goal?.title}"
        />
      {/if}
    </div>
  {/if}

  {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
    <div class="form-group my-4">
      <label for="description" class="form-label">Beskrivelse/tilbakemelding</label>
      <textarea
        id="description"
        class="form-control rounded-0 border-2 border-primary"
        bind:value={localObservation.masteryDescription}
        placeholder="Kort beskrivelse av elevens mestringsnivå"
        rows="4"
      ></textarea>
    </div>
  {/if}

  {#if masterySchema?.config?.isFeedforwardInputEnabled}
    <div class="form-group mb-3">
      <label for="feedforward" class="form-label">Fremovermelding</label>
      <textarea
        id="feedforward"
        class="form-control rounded-0 border-2 border-primary"
        bind:value={localObservation.feedforward}
        placeholder="Konkret, hva kan eleven gjøre for å forbedre seg?"
        rows="4"
      ></textarea>
    </div>
  {/if}

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
