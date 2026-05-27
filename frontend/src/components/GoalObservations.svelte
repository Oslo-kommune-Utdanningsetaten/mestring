<script lang="ts">
  import type { ObservationType, SubjectType, UserType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import { fetchGoalsForSubjectAndStudent, isNumber } from '../utils/functions'
  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'

  import AuthorInfo from './AuthorInfo.svelte'
  import ButtonIcon from './ButtonIcon.svelte'

  const { subject, student, goal } = $props<{
    subject: SubjectType
    student: UserType
    goal: GoalDecorated
  }>()

  let masterySchema = $derived($dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId))

  const isMasteryValueAvailable = (observation: ObservationType): boolean => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return false
    }
    return masterySchema?.config?.isMasteryValueInputEnabled
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
    return getMasteryLevelColorByValue(observation.masteryValue as number, masterySchema)
  }

  const handleViewObservation = (observation: ObservationType) => {
    console.log('Viewing observation', observation)
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
      <div class="student-observations-row observation-item">
        <span>
          <AuthorInfo item={observation} />
        </span>
        <span
          class="px-1"
          style="background-color: {getMasteryLevelColor(observation) ?? 'inherit'}"
        >
          {getMasteryLevelTitle(observation)}
          {#if isMasteryValueAvailable(observation)}
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
          {#if $hasUserAccessToFeature( 'observation', 'update', { groupId: goal.groupId, createdById: observation.createdById } )}
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

<style>
  div.observation-item > span {
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.95rem;
    letter-spacing: -0.07em;
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
