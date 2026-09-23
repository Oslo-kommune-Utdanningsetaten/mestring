<script lang="ts">
  import type { StatusType, UserType, SubjectType } from '../../generated/types.gen'
  import { statusDestroy } from '../../generated/sdk.gen'

  import { hasUserAccessToFeature } from '../../stores/access'
  import { addAlert } from '../../stores/alerts'
  import { trackEvent } from '../../stores/analytics'
  import { t } from '../../stores/translations'
  import { dataStore } from '../../stores/data'
  import { getPreferredStatusCategory } from '../../stores/localStorageFunctions'
  import { calculateSchoolYearMilestones } from '../../utils/schoolYear'

  import StatusEdit from './StatusEdit.svelte'
  import Offcanvas from '../Offcanvas.svelte'
  import ButtonIcon from '../ButtonIcon.svelte'
  import ButtonMini from '../ButtonMini.svelte'

  const { status, student, subject, onRefreshRequired, widgets, disabledWidgets, buttonSize } =
    $props<{
      status?: StatusType
      student?: UserType
      subject?: SubjectType
      onRefreshRequired: Function
      widgets: Array<'create' | 'update' | 'delete' | 'view'>
      disabledWidgets?: Array<'create' | 'update' | 'delete' | 'view'>
      buttonSize?: 'small' | 'large'
    }>()

  let statusWip = $state<StatusType | {} | null>(null)
  let isStatusEditorOpen = $state<boolean>(false)

  const { startAt } = calculateSchoolYearMilestones()
  const today = new Date()
  const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)

  // return YYYY-MM-DD which is latest of start of the school year or sixty days ago
  const getBeginAt = () => {
    return new Date(startAt) > sixtyDaysAgo ? startAt : sixtyDaysAgo.toISOString().split('T')[0]
  }

  const getTitleForWidget = (widget: 'create' | 'update' | 'delete' | 'view') => {
    switch (widget) {
      case 'create':
        return 'Legg til ny ' + t('status', { form: 'sin-indef' })
      case 'update':
        return 'Rediger ' + t('status', { form: 'sin-indef' })
      case 'delete':
        return 'Slett ' + t('status', { form: 'sin-indef' })
      case 'view':
        return 'Vis ' + t('status', { form: 'sin-indef' })
      default:
        return 'unknown widget: ' + widget
    }
  }

  const handleViewStatus = () => {
    console.log('View status clicked, but it is not implemented yet')
  }

  const handleCreateStatus = async () => {
    // open the status editor with prefilled values
    statusWip = {
      subjectId: subject?.id,
      studentId: student.id,
      schoolId: $dataStore.currentSchool.id,
      categoryId: getPreferredStatusCategory(),
      beginAt: getBeginAt(),
      endAt: today.toISOString().split('T')[0],
    }
    isStatusEditorOpen = true
  }

  const handleUpdateStatus = () => {
    statusWip = { ...status }
    isStatusEditorOpen = true
  }

  const handleDeleteStatus = async () => {
    try {
      await statusDestroy({ path: { id: status.id } })
      addAlert({
        type: 'success',
        message: 'Slettet ' + t('status', { form: 'sin-indef' }),
      })
      trackEvent('Status', 'Delete')
      if (!location.pathname.includes('/statuses/risk')) {
        // If not on the /statuses/risk paage, navigate back
        window.history.back()
      }
    } catch (error) {
      console.error('Error deleting status:', error)
      addAlert({
        type: 'danger',
        message:
          'Kunne ikke slette ' +
          t('status', { form: 'sin-indef' }) +
          '. Hvis du mener dette er en feil, kontakt support.',
      })
    }
  }
</script>

<span class="status-widgets">
  <!-- View status widget -->
  {#if widgets.includes('view')}
    <ButtonIcon
      options={{
        iconName: 'document-text',
        title: getTitleForWidget('view'),
        classes: 'bordered',
        disabled: disabledWidgets?.includes('view'),
        onClick: () => handleViewStatus(),
      }}
    />
  {/if}

  <!-- Create status widget -->
  {#if widgets.includes('create') && $hasUserAccessToFeature( 'status', 'create', { subjectId: subject.id, studentGroupIds: student.groupIds } )}
    <ButtonIcon
      options={{
        iconName: 'achievement',
        title: getTitleForWidget('create'),
        classes: 'bordered',
        disabled: disabledWidgets?.includes('create'),
        onClick: () => handleCreateStatus(),
      }}
    />
  {/if}

  <!-- Update status widget -->
  {#if widgets.includes('update') && $hasUserAccessToFeature( 'status', 'update', { subjectId: subject?.id, studentGroupIds: student.groupIds } )}
    {#if buttonSize === 'large'}
      <ButtonMini
        options={{
          iconName: 'document-edit',
          classes: 'my-2 me-2',
          title: getTitleForWidget('update'),
          onClick: () => handleUpdateStatus(),
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
          onClick: () => handleUpdateStatus(),
        }}
      />
    {/if}
  {/if}

  <!-- Delete status widget -->
  {#if widgets.includes('delete') && $hasUserAccessToFeature( 'status', 'delete', { subjectId: subject?.id, studentGroupIds: student.groupIds } )}
    {#key status?.id}
      {#if buttonSize === 'large'}
        <ButtonMini
          options={{
            iconName: 'trash-can',
            classes: 'my-2 me-2',
            title: getTitleForWidget('delete'),
            disabled: disabledWidgets?.includes('delete'),
            onClick: () => handleDeleteStatus(),
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
            onClick: () => handleDeleteStatus(),
            delayActionFor: 3,
          }}
        />
      {/if}
    {/key}
  {/if}
</span>

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  ariaLabel={'Rediger ' + t('status', { form: 'sin-indef' })}
  onClosed={() => {
    statusWip = null
    onRefreshRequired()
  }}
>
  {#if statusWip}
    <StatusEdit
      status={statusWip}
      onDone={() => {
        statusWip = null
        isStatusEditorOpen = false
        onRefreshRequired()
      }}
    />
  {/if}
</Offcanvas>

<style>
  .status-widgets {
    display: inline-flex;
    gap: 0.5rem;
  }
</style>
