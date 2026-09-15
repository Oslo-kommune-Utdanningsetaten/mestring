<script lang="ts">
  import type {
    GoalType,
    UserType,
    SubjectType,
    GroupType,
    MasterySchemaType,
  } from '../../generated/types.gen'
  import { goalsDestroy } from '../../generated/sdk.gen'

  import { hasUserAccessToFeature } from '../../stores/access'
  import { addAlert } from '../../stores/alerts'
  import { trackEvent } from '../../stores/analytics'
  import { dataStore, currentSchool } from '../../stores/data'

  import GoalEdit from './GoalEdit.svelte'
  import Offcanvas from '../Offcanvas.svelte'
  import ButtonIcon from '../ButtonIcon.svelte'

  const {
    goal,
    student,
    subject,
    group,
    masterySchema,
    isIndividual,
    isRelevant,
    onRefreshRequired,
    widgets,
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
  }>()

  let goalWip = $state<GoalType | {} | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)

  const getTitleForWidget = (widget: 'create' | 'update' | 'delete' | 'view') => {
    const goalText = isIndividual ? 'individuelt ' : 'gruppe' + 'mål'
    switch (widget) {
      case 'create':
        return 'Legg til nytt ' + goalText
      case 'update':
        return 'Rediger mål ' + goalText
      case 'delete':
        return 'Slett mål ' + goalText
      case 'view':
        return 'Vis mål ' + goalText
      default:
        return 'unknown widget: ' + widget
    }
  }

  const handleViewGoal = () => {
    console.log('View goal clicked')
  }

  const handleCreateGoal = () => {
    goalWip = {
      schoolId: $currentSchool.id,
      studentId: student?.id,
      subjectId: subject?.id,
      groupId: group?.id,
      masterySchemaId: masterySchema?.id || $dataStore.defaultMasterySchema?.id,
      isIndividual: isIndividual ?? false,
      isRelevant: isRelevant ?? true,
    }
    isGoalEditorOpen = true
  }

  const handleUpdateGoal = () => {
    goalWip = { ...goal }
    isGoalEditorOpen = true
  }

  const handleDeleteGoal = async () => {
    try {
      await goalsDestroy({ path: { id: goal.id } })
      addAlert({
        type: 'success',
        message: `Slettet mål`,
      })
      trackEvent('Goals', 'Delete')
      onRefreshRequired()
    } catch (error) {
      console.error('Error deleting goal:', error)
      addAlert({
        type: 'danger',
        message: `Kunne ikke slette mål. Hvis du mener dette er en feil, kontakt support.`,
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
        onClick: () => handleViewGoal(),
      }}
    />
  {/if}

  <!-- Create goal widget -->
  {#if widgets.includes('create') && $hasUserAccessToFeature( 'goal', 'create', { studentGroupIds: student.groupIds, studentId: student.id } )}
    <ButtonIcon
      options={{
        iconName: 'goal',
        title: getTitleForWidget('create'),
        classes: 'bordered',
        onClick: () => handleCreateGoal(),
      }}
    />
  {/if}

  <!-- Update goal widget -->
  {#if widgets.includes('update') && $hasUserAccessToFeature( 'goal', 'update', { createdById: goal.createdById, studentId: student.id, studentGroupIds: student.groupIds } )}
    <ButtonIcon
      options={{
        iconName: 'document-edit',
        title: getTitleForWidget('update'),
        classes: 'bordered',
        onClick: () => handleUpdateGoal(),
      }}
    />
  {/if}

  <!-- Delete goal widget -->
  {#if widgets.includes('delete') && $hasUserAccessToFeature( 'goal', 'delete', { groupId: goal.groupId, createdById: goal.createdById, studentId: student.id } )}
    {#key goal.id}
      <ButtonIcon
        options={{
          iconName: 'trash-can',
          title: getTitleForWidget('delete'),
          classes: 'bordered',
          onClick: () => handleDeleteGoal(),
          delayActionFor: 3,
        }}
      />
    {/key}
  {/if}
</span>

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isGoalEditorOpen}
  ariaLabel="Rediger mål"
  onClosed={() => {
    goalWip = null
    onRefreshRequired()
  }}
>
  {#if goalWip}
    <GoalEdit
      goal={goalWip}
      {student}
      isGoalIndividual={true}
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
