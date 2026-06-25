<script lang="ts">
  import type { ObservationType, SubjectType, UserType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { getContrastFriendlyTextColor, isNumber } from '../utils/functions'
  import { hasUserAccessToFeature } from '../stores/access'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'
  import { addAlert } from '../stores/alerts'

  import Offcanvas from './Offcanvas.svelte'
  import ObservationView from './ObservationView.svelte'
  import AuthorInfo from './AuthorInfo.svelte'
  import ButtonIcon from './ButtonIcon.svelte'

  const { subject, student, goal } = $props<{
    subject: SubjectType
    student: UserType
    goal: GoalDecorated
  }>()

  let masterySchema = $derived($dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId))
  let observationWip = $state<ObservationType | {} | null>(null)
  let isObservationEditorOpen = $state<boolean>(false)
  let isObservationViewerOpen = $state<boolean>(false)

  const isMasteryValueVisible = (observation: ObservationType): boolean => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return false
    }
    return masterySchema?.config?.isMasteryValueVisible ?? false
  }

  const getMasteryLevelTitle = (observation: ObservationType): string | null => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return null
    }
    return getMasteryTitleByValue(observation.masteryValue as number, masterySchema)
  }

  const getMasteryLevelColor = (observation: ObservationType): string | null => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return null
    }
    return getMasteryLevelColorByValue(observation.masteryValue as number, masterySchema, 0.7)
  }

  const handleViewObservation = (observation: ObservationType) => {
    console.log('Viewing observation', observation)
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

  const handleEditObservation = (observation: ObservationType) => {
    console.log('Editing observation', observation)
  }

  const handleDeleteObservation = async (observationId: string) => {
    console.log('Deleting observation', observationId)
  }
</script>

<div class="goal-secondary-row">
  {#if goal.observations?.length}
    {#each goal?.observations as observation, index}
      {@const bgColor = getMasteryLevelColor(observation) ?? 'inherit'}
      {@const color = getContrastFriendlyTextColor(bgColor)}
      <div class="student-observations-row observation-item">
        <span>
          <AuthorInfo item={observation} />
        </span>
        <span class="masteryLevelTitle" style="background-color: {bgColor}; color: {color};">
          {getMasteryLevelTitle(observation)}
          {#if isMasteryValueVisible(observation)}
            [{observation.masteryValue}]
          {/if}
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
          {#if $hasUserAccessToFeature( 'observation', 'update', { groupId: goal.groupId, createdById: observation.createdById } )}
            {#if index === goal?.observations.length - 1}
              <ButtonIcon
                options={{
                  iconName: 'edit',
                  title: 'Rediger observasjon',
                  classes: 'bordered',
                  onClick: () => handleEditObservation(observation),
                }}
              />
            {/if}
          {/if}
          {#if $hasUserAccessToFeature( 'observation', 'delete', { groupId: goal.groupId, createdById: observation.createdById } )}
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
  {#if observationWip}
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

  .masteryLevelTitle {
    padding: 0 0.25rem;
    display: inline-block;
  }

  .student-observations-row > span:last-child {
    justify-self: end;
  }
</style>
