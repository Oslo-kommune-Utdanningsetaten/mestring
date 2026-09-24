<script lang="ts">
  import type {
    GoalType,
    UserType,
    SubjectType,
    GroupType,
    MasterySchemaType,
  } from '../../generated/types.gen'
  import { goalsDestroy, goalsCreate } from '../../generated/sdk.gen'

  import { hasUserAccessToFeature } from '../../stores/access'
  import { addAlert } from '../../stores/alerts'
  import { trackEvent } from '../../stores/analytics'
  import { dataStore, currentSchool } from '../../stores/data'
  import { t } from '../../stores/translations'

  import GoalEdit from './GoalEdit.svelte'
  import Offcanvas from '../Offcanvas.svelte'
  import ButtonIcon from '../ButtonIcon.svelte'
  import ButtonMini from '../ButtonMini.svelte'

  const {
    goal,
    student,
    subject,
    group,
    masterySchema,
    isIndividual,
    isRelevant,
    sortOrder,
    onRefreshRequired,
    widgets,
    disabledWidgets,
    buttonSize,
  } = $props<{
    goal?: GoalType
    student?: UserType
    subject?: SubjectType
    group?: GroupType
    masterySchema?: MasterySchemaType
    isIndividual?: Boolean
    isRelevant?: Boolean
    sortOrder?: number
    onRefreshRequired: Function
    widgets: Array<'create' | 'update' | 'delete' | 'view'>
    disabledWidgets?: Array<'create' | 'update' | 'delete' | 'view'>
    buttonSize?: 'small' | 'large'
  }>()

  let goalWip = $state<GoalType | {} | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)

  const getTitleForWidget = (widget: 'create' | 'update' | 'delete' | 'view') => {
    const goalText =
      (isIndividual ? 'individuelt ' : 'gruppe') +
      t('goal', { form: 'sin-indef' }) +
      (subject?.displayName ? ' i ' + subject?.displayName.toLowerCase() : '')
    switch (widget) {
      case 'create':
        return 'Legg til nytt ' + goalText
      case 'update':
        return 'Rediger ' + goalText
      case 'delete':
        return 'Slett ' + goalText
      case 'view':
        return 'Vis ' + goalText
      default:
        return 'unknown widget: ' + widget
    }
  }

  const handleViewGoal = () => {
    console.log('View goal clicked')
  }

  const handleCreateGoal = async () => {
    const newGoal = {
      schoolId: $currentSchool.id,
      studentId: student?.id,
      subjectId: subject?.id,
      groupId: group?.id,
      sortOrder: sortOrder ?? 1,
      masterySchemaId: masterySchema?.id || $dataStore.defaultMasterySchema?.id,
      isIndividual: isIndividual ?? false,
      isRelevant: isRelevant ?? true,
    }

    // If all stars are aligned, just create the goal instantly instead of exposing the user to the form
    const createInstantly =
      !$dataStore.currentSchool.isGoalTitleEnabled &&
      !!$dataStore.defaultMasterySchema?.id &&
      !!subject.id

    if (createInstantly) {
      await goalsCreate({
        body: newGoal,
      })
      trackEvent('Goals', 'Create', 'type', 2)
      return onRefreshRequired()
    } else {
      // open the goal editor with prefilled values
      goalWip = newGoal
      isGoalEditorOpen = true
    }
  }

  const handleUpdateGoal = () => {
    goalWip = { ...goal, subjectId: subject?.id }
    isGoalEditorOpen = true
  }

  const handleDeleteGoal = async () => {
    try {
      await goalsDestroy({ path: { id: goal.id } })
      addAlert({
        type: 'success',
        message: `Slettet ${t('goal', { form: 'sin-indef' })}`,
      })
      trackEvent('Goals', 'Delete')
      onRefreshRequired()
    } catch (error) {
      console.error('Error deleting goal:', error)
      addAlert({
        type: 'danger',
        message: `Kunne ikke slette ${t('goal', { form: 'sin-indef' })}. Hvis du mener dette er en feil, kontakt support.`,
      })
    }
  }
</script>

<span class="goal-widgets">
  <!-- View goal widget -->
  {#if widgets.includes('view')}
    <ButtonIcon
      options={{
        iconName: 'document-text',
        title: getTitleForWidget('view'),
        classes: 'bordered',
        disabled: disabledWidgets?.includes('view'),
        onClick: () => handleViewGoal(),
      }}
    />
  {/if}

  <!-- Create goal widget -->
  {#if widgets.includes('create') && $hasUserAccessToFeature( 'goal', 'create', { studentGroupIds: student?.groupIds, studentId: student?.id } )}
    <ButtonIcon
      options={{
        iconName: 'goal',
        title: getTitleForWidget('create'),
        classes: 'bordered',
        disabled: disabledWidgets?.includes('create'),
        onClick: () => handleCreateGoal(),
      }}
    />
  {/if}

  <!-- Update goal widget -->
  {#if widgets.includes('update') && $hasUserAccessToFeature( 'goal', 'update', { createdById: goal.createdById, studentId: student?.id, studentGroupIds: student?.groupIds } )}
    {#if buttonSize === 'large'}
      <ButtonMini
        options={{
          iconName: 'edit',
          classes: 'my-2 me-2',
          title: getTitleForWidget('update'),
          onClick: () => handleUpdateGoal(),
          variant: 'icon-left',
          skin: 'secondary',
          disabled: disabledWidgets?.includes('update'),
        }}
      >
        {getTitleForWidget('update')}
      </ButtonMini>
    {:else}
      <ButtonIcon
        options={{
          iconName: 'document-edit',
          title: getTitleForWidget('update'),
          classes: 'bordered',
          disabled: disabledWidgets?.includes('update'),
          onClick: () => handleUpdateGoal(),
        }}
      />
    {/if}
  {/if}

  <!-- Delete goal widget -->
  {#if widgets.includes('delete') && $hasUserAccessToFeature( 'goal', 'delete', { groupId: goal.groupId, createdById: goal.createdById, studentId: student?.id } )}
    {#key goal.id}
      {#if buttonSize === 'large'}
        <ButtonMini
          options={{
            iconName: 'trash-can',
            classes: 'my-2 me-2',
            title: getTitleForWidget('delete'),
            disabled: disabledWidgets?.includes('delete'),
            onClick: () => handleDeleteGoal(),
            variant: 'icon-left',
            skin: 'secondary',
            delayActionFor: 3,
          }}
        >
          {getTitleForWidget('delete')}
        </ButtonMini>
      {:else}
        <ButtonIcon
          options={{
            iconName: 'trash-can',
            title: getTitleForWidget('delete'),
            classes: 'bordered',
            disabled: disabledWidgets?.includes('delete'),
            onClick: () => handleDeleteGoal(),
            delayActionFor: 3,
          }}
        />
      {/if}
    {/key}
  {/if}
</span>

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isGoalEditorOpen}
  ariaLabel={`Rediger ${t('goal', { form: 'sin-indef' })}`}
  onClosed={() => {
    goalWip = null
    onRefreshRequired()
  }}
>
  {#if goalWip}
    <GoalEdit
      goal={goalWip}
      {group}
      {student}
      isGoalIndividual={isIndividual}
      onDone={() => {
        goalWip = null
        isGoalEditorOpen = false
        onRefreshRequired()
      }}
    />
  {/if}
</Offcanvas>

<style>
  .goal-widgets {
    display: inline-flex;
    gap: 0.5rem;
  }
</style>
