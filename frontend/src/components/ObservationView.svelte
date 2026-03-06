<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore, currentUser } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'
  import AuthorInfo from './AuthorInfo.svelte'

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

  const renderDirection = (): 'horizontal' | 'vertical' | 'unknown' => {
    return masterySchema?.config?.renderDirection || 'unknown'
  }

  let localObservation = $state<Partial<ObservationType> & { masteryValue: number }>({
    masteryValue: calculations.defaultValue,
  })

  // Update localObservation when observation prop changes
  $effect(() => {
    localObservation = {
      ...observation,
    }
  })
</script>

<div class="observation-edit p-4">
  {#if observation}
    <h3 class="pb-2">Observasjon</h3>
    <div class="text-muted">
      <AuthorInfo item={observation} />
    </div>
    <hr />
    <div>
      <span class="text-muted">Elev:</span>
      <span>
        {student.name}
      </span>
    </div>
    <div>
      <span class="text-muted">Mål:</span>
      <span>
        {goal?.title || goal.sortOrder}
      </span>
    </div>

    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      {#if renderDirection() === 'vertical'}
        <ValueInputVertical
          {masterySchema}
          bind:masteryValue={localObservation.masteryValue}
          label=""
          isInputEnabled={false}
        />
      {:else}
        <ValueInputHorizontal
          {masterySchema}
          bind:masteryValue={localObservation.masteryValue}
          label=""
          isInputEnabled={false}
        />
      {/if}
    {/if}

    {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="form-group mb-5">
        <h4 class="mb-2">Beskrivelse/tilbakemelding</h4>
        <p>{localObservation.masteryDescription}</p>
      </div>
    {/if}

    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="form-group mb-3">
        <h4 class="mb-2">Fremovermelding</h4>
        <p>{localObservation.feedforward}</p>
      </div>
    {/if}

    <div class="mt-4">
      <ButtonMini
        options={{
          title: 'Avbryt',
          iconName: 'close',
          skin: 'secondary',
          variant: 'label-only',
          onClick: () => onDone(),
        }}
      >
        Lukk
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
