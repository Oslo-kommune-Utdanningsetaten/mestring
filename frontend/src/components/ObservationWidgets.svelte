<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { ObservationType, GoalType } from '../generated/types.gen'
  import { hasUserAccessToFeature } from '../stores/access'

  import Link from './Link.svelte'
  import ButtonIcon from './ButtonIcon.svelte'

  const {
    observation,
    goal,
    isEditable,
    onViewObservation,
    onEditObservation,
    onDeleteObservation,
  } = $props<{
    observation: ObservationType
    goal: GoalType
    isEditable: Boolean
    onViewObservation: (observation: any, goal: GoalType) => void
    onEditObservation: (observation: any, goal: GoalType) => void
    onDeleteObservation: (observationId: string) => void
  }>()
</script>

<span>
  <ButtonIcon
    options={{
      iconName: 'eye',
      title: 'Se observasjon',
      classes: 'bordered',
      onClick: () => onViewObservation(observation, goal),
    }}
  />

  {#if observation.productUrl}
    <Link
      to={observation.productUrl}
      iconName="link"
      title="Lenke til elevprodukt"
      classes="bordered"
    />
  {/if}

  {#if $hasUserAccessToFeature( 'observation', 'update', { groupId: goal.groupId, createdById: observation.createdById } )}
    {#if isEditable}
      <ButtonIcon
        options={{
          iconName: 'edit',
          title: 'Rediger observasjon',
          classes: 'bordered',
          onClick: () => onEditObservation(observation, goal),
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
          onClick: () => onDeleteObservation(observation.id),
          delayActionFor: 3,
        }}
      />
    {/key}
  {/if}
</span>

<style>
</style>
