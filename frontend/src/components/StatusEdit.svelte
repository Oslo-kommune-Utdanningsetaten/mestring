<script lang="ts">
  import { onMount } from 'svelte'
  import type {
    StatusType,
    SubjectType,
    UserType,
    ObservationType,
    GoalType,
    StatusCategoryType,
  } from '../generated/types.gen'
  import { statusCreate, statusUpdate, usersRetrieve } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig, GoalDecorated } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import {
    fetchGoalsForSubjectAndStudent,
    formatMonthName,
    calculateSchoolYearMilestones,
    subjectsInCommon,
  } from '../utils/functions'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'
  import ButtonMini from './ButtonMini.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import MasteryValueInput from './MasteryValueInput.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import MasteryBarChart from './MasteryBarChart.svelte'
  import { localStorage } from '../stores/localStorage'

  let { status, student, onDone } = $props<{
    status: Partial<StatusType>
    student?: UserType | null
    onDone: () => void
  }>()

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')
  let localStudent = $state<UserType | null>(null)
  let selectableSubjects = $derived(
    subjectsInCommon($dataStore.currentUser, localStudent!, $dataStore.subjects)
  )
  let subject = $derived(
    status.subjectId && selectableSubjects?.find((s: SubjectType) => s.id === status.subjectId)
  )
  let localStatus = $state<Partial<StatusType> & { masteryValue?: number | null }>(
    status
      ? {
          ...status,
          categoryId: status.categoryId || localStorage('preferredStatusCategoryId').get(),
          // Convert ISO timestamps to YYYY-MM-DD format for date inputs
          beginAt: status.beginAt ? status.beginAt.split('T')[0] : undefined,
          endAt: status.endAt ? status.endAt.split('T')[0] : undefined,
        }
      : null
  )
  let localGoals = $state<GoalDecorated[] | null>([])
  let isGoalSectionExpanded = $state<boolean>(false)

  let selectableStatusCategories = $derived(
    $dataStore.statusCategories.filter(
      // If status has a subjectId, only show subject-specific categories
      // If it doesn't, only show non-subject-specific categories
      (cat: StatusCategoryType) => !!localStatus.subjectId === cat.isSubjectSpecific
    )
  )

  const goalSectionToggleOptions = $derived.by(() => {
    return {
      iconName: `chevron-thin-${isGoalSectionExpanded ? 'up' : 'down'}`,
      title: `${isGoalSectionExpanded ? 'Skjul' : 'Vis'} mål`,
      onClick: () => toggleGoalsExpansion(),
    }
  })

  let currentStatusCategory = $derived(
    selectableStatusCategories.find(cat => cat.id === localStatus.categoryId)
  )

  let currentMasterySchema: MasterySchemaWithConfig = $derived.by(() => {
    const schemaId = localStatus.masterySchemaId || currentStatusCategory?.masterySchemaId
    return (
      $dataStore.masterySchemas.find(ms => ms.id === schemaId) || $dataStore.defaultMasterySchema
    )
  })

  const calculations = $derived(useMasteryCalculations(currentMasterySchema))
  let validationErrors = $state<{ beginAt?: string; endAt?: string }>({})

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const fetchStudentData = async () => {
    const userResult = await usersRetrieve({ path: { id: status.studentId } })
    const currentSchoolId = $dataStore.currentSchool?.id
    localStudent = userResult.data!
    if (!localStudent) return
    localGoals = await fetchGoalsForSubjectAndStudent(
      subject.id,
      localStudent.id,
      currentSchoolId,
      $dataStore.currentUser.allGroups
    )
  }

  const generateTitle = (beginAt: string, endAt: string): string => {
    if (currentStatusCategory) {
      return currentStatusCategory.title
    }
    const beginMonth = formatMonthName(beginAt)
    const endMonth = formatMonthName(endAt)
    return `${beginMonth} - ${endMonth}`
  }

  const handleGenerateTitle = () => {
    localStatus = {
      ...localStatus,
      title: generateTitle(localStatus.beginAt!, localStatus.endAt!),
      masteryValue: localStatus?.masteryValue ?? calculations.defaultValue,
    }
  }

  const handleCategoryChange = () => {
    if (currentStatusCategory) {
      // category has been selected, save preference and update fields accordingly
      localStorage('preferredStatusCategoryId').set(currentStatusCategory.id)
      localStatus.title = currentStatusCategory.title
      if (localStatus.masterySchemaId !== currentStatusCategory.masterySchemaId) {
        localStatus.masterySchemaId = currentStatusCategory.masterySchemaId
        localStatus.masteryValue = null // Reset mastery value when category changes, as the scale might be different
      }
      const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones()
      if (currentStatusCategory.name === 'endyear') {
        // Standpunkt
        localStatus.beginAt = startAt
        localStatus.endAt = endAt
      } else if (currentStatusCategory.name === 'midyear') {
        // Halvtårs
        localStatus.beginAt = startAt
        localStatus.endAt = midyearAt
      } else if (currentStatusCategory.name === 'risk') {
        // IVF/G
        localStatus.beginAt = startAt
        localStatus.endAt = endAt
        localStatus.subjectId = null // Unset subject for risk status category
      } else {
        console.error('Unknown category', { currentStatusCategory })
      }
    } else {
      // category has been unset, remove preference and reset related fields
      localStorage('preferredStatusCategoryId').remove()
      localStatus.title = null
      localStatus.masterySchemaId = null
      localStatus.subjectId = subject?.id // Restore subject when category is unset
    }
  }

  const toggleGoalsExpansion = () => {
    isGoalSectionExpanded = !isGoalSectionExpanded
  }

  const handleSave = async () => {
    validationErrors = {}
    if (!localStatus.beginAt) {
      validationErrors.beginAt = 'Fra-dato er påkrevd'
    }
    if (!localStatus.endAt) {
      validationErrors.endAt = 'Til-dato er påkrevd'
    }
    if (localStatus.beginAt && localStatus.endAt) {
      const beginDate = new Date(localStatus.beginAt)
      const endDate = new Date(localStatus.endAt)
      if (beginDate > endDate) {
        validationErrors.endAt = 'Til-dato må være etter Fra-dato'
      }
    }
    // Stop if validation fails
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    localStatus.studentId = localStudent?.id
    localStatus.schoolId = $dataStore.currentSchool?.id
    localStatus.title =
      localStatus.title?.trim() || generateTitle(localStatus.beginAt!, localStatus.endAt!)
    let action = undefined

    try {
      if (localStatus.id) {
        await statusUpdate({
          path: { id: localStatus.id },
          body: localStatus as any,
        })
        trackEvent('Status', 'Update')
        action = 'Oppdaterte'
      } else {
        await statusCreate({
          body: localStatus as any,
        })
        trackEvent('Status', 'Create')
        action = 'Opprettet ny'
      }
      addAlert({
        type: 'success',
        message: `${action} status for ${localStudent?.name}.`,
      })
      onDone()
    } catch (error) {
      console.error('Error saving status:', error)
      addAlert({
        type: 'danger',
        message: `Noe gikk galt ved lagring av status for ${localStudent?.name}.`,
      })
    }
  }

  $effect(() => {
    if (!student) {
      fetchStudentData()
    }
  })
</script>

<div class="status-edit px-4 py-2">
  <h2 class="my-4">
    {localStatus.id ? 'Redigerer' : 'Opprett ny'} status for
    <mark>{localStudent?.name}</mark>
  </h2>

  {#if localStatus && localStudent}
    <!-- Goals, compacted for reference -->
    {#if subject}
      <div class="my-5 goals-section">
        <h3>
          Elevens mål i <mark>{subject?.shortName || subject?.displayName}</mark>
          <ButtonIcon options={goalSectionToggleOptions} />
        </h3>
        {#if !localGoals}
          <p><em>Eleven har ingen mål i dette faget</em></p>
        {/if}

        {#if localGoals && isGoalSectionExpanded}
          <div class="goals-container mt-2">
            {#each localGoals as goal}
              <div class="goal-row">
                <span class="goal-sort-order">{goal.sortOrder}</span>
                {#if goal.isIndividual}
                  <span class="individual-goal-icon" title="Individuelt mål">
                    <pkt-icon name="person"></pkt-icon>
                  </span>
                {:else}
                  <span class="group-goal-icon" title="Gruppemål">
                    <pkt-icon name="group"></pkt-icon>
                  </span>
                {/if}

                <!-- Goal title -->
                {#if $dataStore.currentSchool.isGoalTitleEnabled}
                  <span class="goal-title">
                    {goal.title}
                  </span>
                {/if}

                <!-- Stats widgets -->
                <span class="goal-stats">
                  {#if goal.masteryData}
                    <MasteryLevelBadge
                      masteryData={goal.masteryData}
                      masterySchema={getMasterySchmemaForGoal(goal)}
                    />
                    {#if $isMasteryBarChartVisible}
                      <MasteryBarChart
                        data={goal.observations?.map((o: ObservationType) => o.masteryValue)}
                        masterySchema={getMasterySchmemaForGoal(goal)}
                      />
                    {/if}
                  {:else}
                    Ingen observasjoner i dette målet
                  {/if}
                </span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    <!-- Subject -->
    {#if subject}
      <div class="d-flex my-5">
        <h3 class="col-4 mb-0">Fag</h3>
        <div class="col-8">
          {subject.shortName || subject.displayName || subject.grepCode}
        </div>
      </div>
    {/if}

    <!-- Kategori -->
    <div class="d-flex my-5">
      <h3 class="col-4 mb-0">Kategori</h3>
      <div class="col-8">
        <label for="categorySelect" class="mb-1 visually-hidden">Kategori</label>
        <select
          class="pkt-input"
          id="categorySelect"
          bind:value={localStatus.categoryId}
          onchange={handleCategoryChange}
        >
          <option value={null} selected={!localStatus.categoryId}>Ingen</option>
          {#each selectableStatusCategories as statusCategory}
            <option
              value={statusCategory.id}
              selected={statusCategory.id === localStatus.categoryId}
            >
              {statusCategory.title}
            </option>
          {/each}
        </select>
      </div>
    </div>

    <!-- Begin and end dates -->
    <div class="d-flex my-5">
      <h3 class="col-4">Periode</h3>
      <div class="col-auto">
        <label for="beginAt" class="form-label mb-0">Fra</label>
        <input
          id="beginAt"
          type="date"
          class="form-control date-input"
          class:is-invalid={validationErrors.beginAt}
          bind:value={localStatus.beginAt}
          required
        />
        {#if validationErrors.beginAt}
          <div class="invalid-feedback d-block">{validationErrors.beginAt}</div>
        {/if}
      </div>
      <div class="col-auto ms-3">
        <label for="endAt" class="form-label mb-0">Til</label>
        <input
          id="endAt"
          type="date"
          class="form-control date-input"
          class:is-invalid={validationErrors.endAt}
          bind:value={localStatus.endAt}
          required
        />
        {#if validationErrors.endAt}
          <div class="invalid-feedback d-block">{validationErrors.endAt}</div>
        {/if}
      </div>
    </div>

    <!-- Title -->
    <div class="d-flex my-5">
      <h3 class="col-4">Tittel</h3>
      <div class="col-8">
        <label for="title" class="visually-hidden">Tittel</label>
        <div class="input-with-icon">
          <input
            id="title"
            type="text"
            class="form-control rounded-0 border-2 border-primary p-2"
            bind:value={localStatus.title}
            placeholder="Angi en tittel"
          />
          <ButtonIcon
            options={{
              iconName: 'arrow-circle',
              title: 'Foreslå tittel basert på datoer',
              onClick: () => handleGenerateTitle(),
            }}
          />
        </div>
      </div>
    </div>

    <!-- Mastery value input -->
    {#if currentMasterySchema?.config?.isMasteryValueInputEnabled}
      <div class="d-flex my-5">
        <h3 class="col-4">Mestring</h3>
        <div class="col-8">
          <MasteryValueInput
            masterySchema={currentMasterySchema}
            bind:value={localStatus.masteryValue}
          />
        </div>
      </div>
    {/if}

    <!-- Mastery description input -->
    {#if currentMasterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="d-flex my-5">
        <h3 class="col-4">Beskrivelse</h3>
        <div class="col-8">
          <label for="description" class="visually-hidden">
            Beskrivelse av elevens mestringsnivå
          </label>
          <textarea
            id="description"
            class="form-control rounded-0 border-2 border-primary p-2"
            bind:value={localStatus.masteryDescription}
            placeholder="Kort beskrivelse av elevens mestringsnivå"
            rows="4"
          ></textarea>
        </div>
      </div>
    {/if}

    <!-- Mastery feed forward input -->
    {#if currentMasterySchema?.config?.isFeedforwardInputEnabled}
      <div class="d-flex my-5">
        <h3 class="col-4">Fremovermelding</h3>
        <div class="col-8">
          <label for="feedforward" class="visually-hidden">Fremovermelding til eleven</label>
          <textarea
            id="feedforward"
            class="form-control rounded-0 border-2 border-primary p-2"
            bind:value={localStatus.feedforward}
            placeholder="Konkret, hva kan eleven gjøre for å forbedre seg?"
            rows="4"
          ></textarea>
        </div>
      </div>
    {/if}

    <div class="d-flex gap-2 justify-content-start mt-2">
      <ButtonMini
        options={{
          title: 'Lagre',
          skin: 'primary',
          variant: 'label-only',
          classes: 'me-2',
          onClick: () => handleSave(),
        }}
      >
        Lagre
      </ButtonMini>

      <ButtonMini
        options={{
          title: 'Avbryt',
          skin: 'secondary',
          variant: 'label-only',
          onClick: () => onDone(),
        }}
      >
        Avbryt
      </ButtonMini>
    </div>
  {:else}
    No status...
  {/if}
</div>

<style>
  .status-edit {
    width: 100%;
    max-width: 100%;
  }

  .date-input {
    border-width: 2px;
    border-color: var(--pkt-color-primary);
    border-radius: 0px;
    padding-left: 8px;
    max-width: 12rem;
  }

  .input-with-icon {
    position: relative;
  }

  .input-with-icon input {
    padding-right: 2.5rem;
  }

  .input-with-icon :global(.button-icon-wrapper) {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
  }

  .goals-section {
    background-color: var(--pkt-color-brand-neutrals-200);
    padding: 0.5rem;

    h3 {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-transform: uppercase;
      font-size: 0.8rem;
    }
  }

  .goals-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .goal-row {
    display: grid;
    grid-template-columns: auto auto minmax(max-content, 30ch) 1fr;
    gap: 1rem;
    align-items: stretch;
    padding: 0.5rem 1rem;
    background-color: white;
    border-radius: 0px;
    min-height: 2rem;
  }

  .goal-row > * {
    display: flex;
    align-items: center;
  }

  .goal-sort-order,
  .individual-goal-icon,
  .group-goal-icon {
    justify-content: center;
  }

  .goal-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .goal-stats {
    gap: 0.5rem;
    justify-content: flex-start;
  }
</style>
