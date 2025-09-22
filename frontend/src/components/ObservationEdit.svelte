<script lang="ts">
  import type { ObservationReadable, GoalReadable, UserReadable } from '../generated/types.gen'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import type { GoalDecorated, MasterySchemaWithConfig } from '../types/models'
  import { dataStore, currentUser } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'

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
    if (observation && observation.id) {
      localObservation = {
        ...observation,
        masteryValue: observation.masteryValue,
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
    localObservation.observerId = $currentUser?.id
    localObservation.observedAt = new Date().toISOString()
    console.log('Saving observation:', localObservation)
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
    <ButtonMini
      options={{
        title: 'Lagre',
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        classes: 'm-2',
        onClick: () => handleSave(),
      }}
    >
      Lagre
    </ButtonMini>

    <ButtonMini
      options={{
        title: 'Avbryt',
        iconName: 'close',
        skin: 'secondary',
        variant: 'label-only',
        classes: 'm-2',
        onClick: () => onDone(),
      }}
    >
      Avbryt
    </ButtonMini>
  </div>
</div>

<style>
</style>
