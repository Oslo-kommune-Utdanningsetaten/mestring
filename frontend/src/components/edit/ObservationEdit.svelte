<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import { observationsCreate, observationsUpdate, observationsList } from '../../generated/sdk.gen'

  import { useMasteryCalculations } from '../../utils/masteryHelpers'
  import { dataStore, currentUser, currentSchool } from '../../stores/data'
  import { localStorage } from '../../stores/localStorage'
  import { getPreferredCreatedParams } from '../../stores/localStorageFunctions'
  import { addAlert } from '../../stores/alerts'
  import { trackEvent } from '../../stores/analytics'
  import { t } from '../../stores/translations'

  import ButtonMini from '../ButtonMini.svelte'
  import MasteryValueInput from '../MasteryValueInput.svelte'

  const {
    student,
    goal,
    observation,
    masterySchema: masterySchemaProp,
    isPersistenceControlEnabled = true,
    onDone,
  }: {
    student: UserType
    goal: GoalType | null
    observation: Partial<ObservationType> & { masteryValue?: number }
    masterySchema?: MasterySchemaWithConfig | null
    isPersistenceControlEnabled?: boolean
    onDone: () => void
  } = $props()

  const isObservationUrlEnabled = localStorage<boolean>('isObservationUrlEnabled')
  const isHistoryVisibleOnMasteryInput = localStorage<boolean>('isHistoryVisibleOnMasteryInput')

  let localObservation = $state<Partial<ObservationType> & { masteryValue?: number }>({})
  let formContainer = $state<HTMLElement | null>(null)
  let observations = $state<ObservationType[]>([])

  const masterySchema: MasterySchemaWithConfig = $derived(
    masterySchemaProp ?? $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))
  const studentFirstName = $derived(student?.name.split(' ')[0] || 'eleven')

  const fetchObservations = async () => {
    try {
      const observationsResult = await observationsList({
        query: {
          school: $currentSchool.id,
          student: student?.id,
          goal: goal?.id,
          ...getPreferredCreatedParams(),
        },
      })
      observations = observationsResult.data || []
      // If the current observation has an id (is being edited) filter out observations from a later date than the current observation,
      if (observation?.id) {
        observations = observations.filter(
          o => observation.createdAt && new Date(o.createdAt) <= new Date(observation.createdAt)
        )
      }
      // sort by createdAt in ascending order
      observations = observations.sort(
        (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      )
    } catch (error) {
      console.error('Error fetching observations:', error)
    }
  }

  $effect(() => {
    if ($isHistoryVisibleOnMasteryInput) {
      fetchObservations()
    }
  })

  // Update localObservation when observation prop changes
  $effect(() => {
    localObservation = {
      ...observation,
      masteryValue: observation?.masteryValue ?? calculations.defaultValue,
    }
  })

  $effect(() => {
    if (formContainer) {
      const id = setTimeout(
        () => formContainer?.querySelector<HTMLElement>('input, textarea')?.focus(),
        300
      )
      return () => clearTimeout(id)
    }
  })

  const handleToggleVisibility = () => {
    localObservation.isVisibleToStudent = !localObservation.isVisibleToStudent
    localObservation = { ...localObservation } // Trigger reactivity
  }

  const handleSave = async () => {
    localObservation.studentId = student?.id
    localObservation.goalId = goal?.id
    let action = undefined
    try {
      if (localObservation.id) {
        await observationsUpdate({
          path: { id: localObservation.id },
          body: localObservation as any,
        })
        trackEvent('Observations', 'Update')
        action = 'Oppdaterte'
      } else {
        localObservation.observedAt = new Date().toISOString() // only set when creating a new observation
        await observationsCreate({
          body: localObservation as any,
        })
        trackEvent('Observations', 'Create')
        action = 'Opprettet ny'
      }
      addAlert({
        type: 'success',
        message: `${action} ${t('observation', { form: 'sin-indef' })} for ${student.name}.`,
      })
      onDone()
    } catch (error) {
      console.error('Error saving Observation:', error)
      addAlert({
        type: 'danger',
        message: `Noe gikk galt ved lagring av ${t('observation', { form: 'sin-indef' })} for ${student.name}.`,
      })
    }
  }
</script>

<div class="observation-edit p-4" bind:this={formContainer}>
  {#if localObservation}
    <h3>
      {localObservation.id ? 'Redigerer' : 'Ny'}
      {t('observation', { form: 'sin-indef' })}
    </h3>

    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      <div class="my-4">
        <MasteryValueInput
          {masterySchema}
          {observations}
          bind:value={localObservation.masteryValue}
          title="Hvor godt mestrer {student?.name} {goal?.title ||
            'dette ' + t('goal', { form: 'sin-def' })}?"
        />
      </div>
    {/if}

    {#if $currentSchool.isServiceEnabledForStudents && !$currentUser.isStudent}
      <pkt-checkbox
        class="ms-auto"
        label={localObservation.isVisibleToStudent ? 'Synlig for eleven' : 'IKKE synlig for eleven'}
        labelPosition="right"
        isSwitch="true"
        aria-checked={localObservation.isVisibleToStudent}
        checked={localObservation.isVisibleToStudent}
        onchange={() => handleToggleVisibility()}
      ></pkt-checkbox>
    {/if}

    {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="form-group">
        <label for="description" class="form-label visually-hidden">
          Beskrivelse/tilbakemelding
        </label>
        <textarea
          id="description"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localObservation.masteryDescription}
          placeholder="Kort beskrivelse av hva {studentFirstName} får til"
          rows="4"></textarea>
      </div>
    {/if}

    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="form-group">
        <label for="feedforward" class="form-label visually-hidden">Fremovermelding</label>
        <textarea
          id="feedforward"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localObservation.feedforward}
          placeholder="Konkret, hva trenger {studentFirstName} nå?"
          rows="4"></textarea>
      </div>
    {/if}

    {#if $isObservationUrlEnabled}
      <div class="form-group">
        <label for="productUrl" class="form-label visually-hidden">Lenke</label>
        <input
          id="goalTitle"
          type="text"
          class="form-control rounded-0 border-2 border-primary input-field"
          bind:value={localObservation.productUrl}
          placeholder="Lenke til prosjekt, produkt, lyd, video el.l."
        />
      </div>
    {/if}

    {#if isPersistenceControlEnabled}
      <div class="d-flex gap-2 justify-content-start mt-4">
        <ButtonMini
          options={{
            title: 'Lagre',
            iconName: 'check',
            skin: 'primary',
            variant: 'label-only',
            classes: 'me-2 mt-2',
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
    {/if}
  {:else}
    No observation...
  {/if}
</div>

<style>
  .observation-edit {
    width: 100%;
    max-width: 100%;
  }

  .form-group {
    margin-top: 2.5rem;
  }

  textarea {
    font-size: 1.2rem;
  }
</style>
