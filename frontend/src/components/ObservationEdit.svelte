<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../generated/types.gen'
  import { observationsCreate, observationsUpdate } from '../generated/sdk.gen'
  import type { GoalDecorated, MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore, currentUser } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'

  const { student, goal, observation, onDone } = $props<{
    student: UserType | null
    goal: GoalType | null
    observation: ObservationType | {} | null
    onDone: () => void
  }>()

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))

  let localObservation = $state<Partial<ObservationType> & { masteryValue: number }>({
    masteryValue: calculations.defaultValue,
  })

  // Update localObservation when observation prop changes
  $effect(() => {
    localObservation = {
      ...observation,
    }
  })

  const renderDirection = (): 'horizontal' | 'vertical' | 'unknown' => {
    return masterySchema?.config?.renderDirection || 'unknown'
  }

  const handleSave = async () => {
    localObservation.studentId = student?.id
    localObservation.goalId = goal?.id
    localObservation.observerId = $currentUser?.id
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
      console.error('Error saving Observation:', error)
    }
  }
</script>

<div class="observation-edit p-4">
  {#if localObservation}
    <h3 class="pb-2">
      {localObservation.id ? 'Redigerer' : 'Ny'} observasjon
    </h3>

    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      <div class="mb-4">
        {#if renderDirection() === 'vertical'}
          <ValueInputVertical
            {masterySchema}
            bind:masteryValue={localObservation.masteryValue}
            label="Hvor ofte mestrer {student?.name} {goal?.title || 'dette målet'}?"
          />
        {:else}
          <ValueInputHorizontal
            {masterySchema}
            bind:masteryValue={localObservation.masteryValue}
            label="Hvor ofte mestrer {student?.name} {goal?.title || 'dette målet'}?"
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
  {:else}
    No observation...
  {/if}
</div>

<style>
  .observation-edit {
    width: 100%;
    max-width: 100%;
  }
</style>
