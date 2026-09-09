<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { ObservationType, GoalType, UserType, SubjectType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { observationsDestroy } from '../generated/sdk.gen'

  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  import Link from './Link.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import ObservationView from './ObservationView.svelte'

  const { observation, goal, student, subject, isEditable, onRefreshRequired, widgets } = $props<{
    observation?: ObservationType
    goal: GoalType
    student: UserType
    subject: SubjectType
    onRefreshRequired?: Function
    widgets: Array<'create' | 'update' | 'delete' | 'view' | 'productUrl'>
  }>()

  let observationWip = $state<ObservationType | {} | null>(null)
  let isObservationEditorOpen = $state<boolean>(false)
  let isObservationViewerOpen = $state<boolean>(false)
  let goalForObservation = $state<GoalDecorated | null>(null)

  const handleCreateObservation = (goal: GoalDecorated) => {
    const prevousObservations = goal?.observations || []
    const previousObservation = prevousObservations[prevousObservations.length - 1]
    // prefill with value from previous observation, minus productUrl
    observationWip = { masteryValue: previousObservation?.masteryValue || null, productUrl: null }
    goalForObservation = { ...goal }
    isObservationEditorOpen = true
  }

  const handleEditObservation = (observation: ObservationType | null, goal: GoalDecorated) => {
    // update existing observation
    observationWip = observation
    goalForObservation = { ...goal }
    isObservationEditorOpen = true
  }

  const handleViewObservation = (observation: ObservationType, goal: GoalType) => {
    if (observation) {
      observationWip = observation
      isObservationViewerOpen = true
      goalForObservation = { ...goal }
    } else {
      addAlert({
        type: 'danger',
        message: 'Kunne ikke finne observasjon. Hvis du mener dette er en feil, kontakt support.',
      })
    }
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      addAlert({
        type: 'success',
        message: `Slettet observasjon`,
      })
      trackEvent('Observations', 'Delete')
      onRefreshRequired()
    } catch (error) {
      console.error('Error deleting observation:', error)
      addAlert({
        type: 'danger',
        message: `Kunne ikke slette observasjon. Hvis du mener dette er en feil, kontakt support.`,
      })
    }
  }
</script>

<span>
  <!-- View observation widget -->
  {#if widgets.includes('view')}
    <ButtonIcon
      options={{
        iconName: 'eye',
        title: 'Se observasjon',
        classes: 'bordered',
        onClick: () => handleViewObservation(observation, goal),
      }}
    />
  {/if}

  <!-- Create observation widget -->
  {#if widgets.includes('create') && $hasUserAccessToFeature( 'observation', 'create', { groupId: goal.groupId, subjectId: subject.id, studentGroupIds: student.groupIds } )}
    <ButtonIcon
      options={{
        iconName: 'bullseye',
        title: 'Ny observasjon',
        classes: 'bordered',
        disabled: !goal.isRelevant,
        onClick: () => handleCreateObservation(goal),
      }}
    />
  {/if}

  <!-- Edit observation widget -->
  {#if widgets.includes('update') && $hasUserAccessToFeature( 'observation', 'update', { groupId: goal.groupId, createdById: observation.createdById } )}
    <ButtonIcon
      options={{
        iconName: 'edit',
        title: 'Rediger observasjon',
        classes: 'bordered',
        onClick: () => handleEditObservation(observation, goal),
      }}
    />
  {/if}

  <!-- Delete observation widget -->
  {#if widgets.includes('delete') && $hasUserAccessToFeature( 'observation', 'update', { groupId: goal.groupId, createdById: observation.createdById } )}
    {#key observation.id}
      <ButtonIcon
        options={{
          iconName: 'trash-can',
          title: 'Slett observasjon',
          classes: 'bordered',
          onClick: () => handleDeleteObservation(observation.id),
          delayActionFor: 3,
        }}
      />
    {/key}
  {/if}

  <!-- Product URL observation widget -->
  {#if widgets.includes('productUrl') && observation.productUrl}
    <Link
      to={observation.productUrl}
      iconName="link"
      title="Lenke til elevprodukt"
      classes="bordered"
    />
  {/if}
</span>

<!-- offcanvas for creating/editing observations -->
<Offcanvas
  bind:isOpen={isObservationEditorOpen}
  ariaLabel="Rediger observasjon"
  onClosed={() => {
    observationWip = null
    onRefreshRequired()
  }}
>
  {#if observationWip}
    <ObservationEdit
      {student}
      observation={observationWip}
      goal={goalForObservation}
      onDone={() => {
        observationWip = null
        isObservationEditorOpen = false
        onRefreshRequired()
      }}
    />
  {/if}
</Offcanvas>

<!-- offcanvas for viewing observations -->
<Offcanvas
  bind:isOpen={isObservationViewerOpen}
  ariaLabel="Se observasjon"
  onClosed={() => {
    observationWip = null
  }}
>
  {#if observationWip}
    <ObservationView
      {student}
      observation={observationWip}
      goal={goalForObservation}
      onDone={() => {
        observationWip = null
        isObservationViewerOpen = false
      }}
    />
  {/if}
</Offcanvas>

<style>
</style>
