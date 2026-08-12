<script lang="ts">
  import type { ObservationType, UserType, GoalType, GroupType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { observationsDestroy } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  import Offcanvas from './Offcanvas.svelte'
  import ObservationView from './ObservationView.svelte'
  import AuthorInfo from './AuthorInfo.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import MasteryLevelTitle from './MasteryLevelTitle.svelte'

  const { student, goal, group, onRefreshNeeded, onEditObservation } = $props<{
    student: UserType
    goal: GoalDecorated
    group: GroupType
    onRefreshNeeded: () => void
    onEditObservation: (observation: ObservationType | null, goal: GoalType) => void
  }>()

  let observationWip = $state<ObservationType | {} | null>(null)
  let isObservationViewerOpen = $state<boolean>(false)
  let masterySchema = $derived($dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId))
  let observations = $derived(
    goal.observations
      ? goal.observations.toSorted((goalA: GoalType, goalB: GoalType) => {
          // sort observations by createdAt ascending
          const dateA = new Date(goalA.createdAt)
          const dateB = new Date(goalB.createdAt)
          return dateA.getTime() - dateB.getTime()
        })
      : []
  )

  const handleViewObservation = (observation: ObservationType) => {
    if (observation) {
      observationWip = observation
      isObservationViewerOpen = true
    } else {
      addAlert({
        type: 'danger',
        message: 'Kunne ikke finne observasjon. Hvis du mener dette er en feil, kontakt support.',
      })
    }
  }

  const handleEditObservation = (observation: ObservationType | null, goal: GoalType) => {
    onEditObservation(observation, goal)
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      addAlert({
        type: 'success',
        message: `Slettet observasjon`,
      })
      trackEvent('Observations', 'Delete')
      onRefreshNeeded()
    } catch (error) {
      console.error('Error deleting observation:', error)
      addAlert({
        type: 'danger',
        message: `Kunne ikke slette observasjon. Hvis du mener dette er en feil, kontakt support.`,
      })
    }
  }
</script>

<div class="goal-secondary-row">
  {#if observations.length}
    {#each observations as observation}
      <div class="student-observations-row observation-item">
        <span>
          <AuthorInfo item={observation} />
        </span>

        <span>
          <MasteryLevelTitle {observation} {masterySchema} />
        </span>

        <span>
          <ButtonIcon
            options={{
              iconName: 'eye',
              title: 'Se observasjon',
              classes: 'bordered',
              onClick: () => handleViewObservation(observation),
            }}
          />
          {#if $hasUserAccessToFeature( 'observation', 'update', { groupId: group.id, studentId: observation.studentId, createdById: observation.createdById, goalStudentId: goal.studentId } )}
            <ButtonIcon
              options={{
                iconName: 'edit',
                title: 'Rediger observasjon',
                classes: 'bordered',
                onClick: () => handleEditObservation(observation, goal),
              }}
            />
          {/if}
          {#if $hasUserAccessToFeature( 'observation', 'delete', { groupId: group.id, studentId: observation.studentId, createdById: observation.createdById, goalStudentId: goal.studentId } )}
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
        </span>
      </div>
    {/each}
  {:else}
    <p>Ingen observasjoner for dette målet.</p>
  {/if}
</div>

<!-- offcanvas for viewing observations -->
<Offcanvas
  bind:isOpen={isObservationViewerOpen}
  ariaLabel="Se observasjon"
  onClosed={() => {
    observationWip = null
  }}
>
  {#if observationWip && isObservationViewerOpen}
    <ObservationView
      {student}
      observation={observationWip}
      {goal}
      masteryTitle=" "
      onDone={() => {
        observationWip = null
        isObservationViewerOpen = false
      }}
    />
  {/if}
</Offcanvas>

<style>
  div.observation-item > span {
    font-size: 0.85rem;
  }

  .goal-secondary-row {
    margin-top: 10px;
    margin-left: 6px;
    padding-left: 20px;
    border-left: 3px solid var(--bs-secondary);
  }

  .student-observations-row {
    display: grid;
    grid-template-columns: 8fr 5fr 4fr;
    column-gap: 0.5rem;
    align-items: center;
  }

  .student-observations-row > span:last-child {
    justify-self: end;
  }
</style>
