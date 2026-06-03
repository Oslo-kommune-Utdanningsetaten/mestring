<script lang="ts">
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
  import { areSchemaValuesConsistent } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import {
    fetchGoalsForSubjectAndStudent,
    formatMonthName,
    formatDateHumanly,
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

  let { status, onDone } = $props<{
    status: Partial<StatusType>
    onDone: () => void
  }>()

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')
  let localStudent = $state<UserType | null>(null)
  let localStatus = $state<Partial<StatusType> & { masteryValue?: number | null }>({ ...status })
  let localGoals = $state<GoalDecorated[] | null>([])
  let isGoalSectionExpanded = $state<boolean>(false)
  let validationErrors = $state<{ beginAt?: string; endAt?: string }>({})

  let selectableSubjects = $derived(
    subjectsInCommon($dataStore.currentUser, localStudent!, $dataStore.subjects)
  )

  let subject = $derived(
    status.subjectId && selectableSubjects?.find((s: SubjectType) => s.id === status.subjectId)
  )

  let selectableStatusCategories = $derived(
    $dataStore.statusCategories.filter(
      // If status has a subjectId, only show subject-specific categories
      // If it doesn't, only show non-subject-specific categories
      (cat: StatusCategoryType) => !!localStatus.subjectId === cat.isSubjectSpecific
    )
  )
  const studentFirstName = $derived(localStudent?.name.split(' ')[0] || 'eleven')

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

  const getMasterySchemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const fetchStudentData = async () => {
    const userResult = await usersRetrieve({ path: { id: status.studentId } })
    const currentSchoolId = $dataStore.currentSchool?.id
    localStudent = userResult.data!
    if (!localStudent || !subject) return
    localGoals = await fetchGoalsForSubjectAndStudent(
      subject.id,
      localStudent.id,
      currentSchoolId,
      $dataStore.currentUser.allGroups
    )
    localStatus = getUpdatedStatus(localStatus)
  }

  const generateTitle = (aStatus: Partial<StatusType>): string => {
    const statusCategory = selectableStatusCategories.find(cat => cat.id === aStatus.categoryId)
    if (statusCategory) {
      const today = new Date()
      let season = ''
      let yearShort = ''
      if (statusCategory.name === 'midyear') {
        season = 'h'
        yearShort = (today.getFullYear() - 1).toString().slice(-2)
      } else if (statusCategory.name === 'endyear') {
        season = 'v'
        yearShort = today.getFullYear().toString().slice(-2)
      } else if (statusCategory.name === 'risk') {
        season = today.getMonth() < 7 ? 'v' : 'h'
        yearShort = today.getFullYear().toString().slice(-2)
      } else {
        console.error('Unknown category', { statusCategory })
      }
      return [statusCategory.title, ' ', season, yearShort].join('')
    }
    const beginMonth = formatMonthName(aStatus.beginAt)
    const endMonth = formatMonthName(aStatus.endAt)
    const result = `${beginMonth} - ${endMonth}`
    return result.charAt(0).toUpperCase() + result.slice(1)
  }

  const handleGenerateTitle = () => {
    localStatus = {
      ...localStatus,
      title: generateTitle(localStatus),
    }
  }

  const handleCategoryChange = () => {
    if (localStatus.categoryId) {
      // category has been selected, save preference
      localStorage('preferredStatusCategoryId').set(localStatus.categoryId)
    } else {
      // category has been unset, remove preference
      localStorage('preferredStatusCategoryId').remove()
    }
    // update fields according to new category
    localStatus = getUpdatedStatus(localStatus)
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
    localStatus.title = localStatus.title?.trim() || generateTitle(localStatus)
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

  const getUpdatedStatus = (aStatus: Partial<StatusType>): Partial<StatusType> => {
    const updatedStatus = { ...aStatus }
    const statusCategory = $dataStore.statusCategories.find(cat => cat.id === aStatus.categoryId)
    if (statusCategory) {
      const currentMasterySchema = $dataStore.masterySchemas.find(
        ms => ms.id === aStatus.masterySchemaId
      )
      const nextMasterySchema = $dataStore.masterySchemas.find(
        ms => ms.id === statusCategory.masterySchemaId
      )
      if (!areSchemaValuesConsistent([currentMasterySchema, nextMasterySchema])) {
        updatedStatus.masteryValue = null // Reset mastery value if schemas are inconsistent
      }
      updatedStatus.title = generateTitle(updatedStatus)
      updatedStatus.masterySchemaId = statusCategory.masterySchemaId

      if (!statusCategory.isSubjectSpecific) {
        updatedStatus.subjectId = null // Unset subject for non-subject-specific category
      }
      const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones()
      if (statusCategory.name === 'midyear') {
        // Halvtårs
        updatedStatus.beginAt = startAt
        updatedStatus.endAt = midyearAt
      } else if (statusCategory.name === 'endyear') {
        // Standpunkt
        updatedStatus.beginAt = startAt
        updatedStatus.endAt = endAt
      } else if (statusCategory.name === 'risk') {
        // IVF/G
        updatedStatus.beginAt = startAt
        updatedStatus.endAt = endAt
      } else {
        console.error('Unknown category', { statusCategory })
      }
    } else {
      updatedStatus.title = null
      updatedStatus.masterySchemaId = $dataStore.defaultMasterySchema.id
      updatedStatus.subjectId = subject?.id
      updatedStatus.beginAt = status.beginAt?.split('T')[0]
      updatedStatus.endAt = status.endAt?.split('T')[0]
    }
    return updatedStatus
  }

  $effect(() => {
    if (status.studentId && !localStudent) {
      fetchStudentData()
    }
  })
</script>

<div class="status-edit">
  <!-- Header -->
  <div class="p-4 pb-3 border-bottom border-3 border-primary">
    <h2 class="fs-5 fw-semibold mb-0">
      {localStatus.id ? 'Redigerer' : 'Ny'} status for
      <mark>{localStudent?.name}</mark>
    </h2>
    {#if localStatus.beginAt || localStatus.endAt}
      <p class="small text-muted mt-1 mb-0">
        {localStatus.title} [{formatDateHumanly(localStatus.beginAt) || '?'} – {formatDateHumanly(
          localStatus.endAt
        ) || '?'}]
      </p>
    {/if}
  </div>

  {#if localStatus && localStudent}
    <div class="p-4">
      <!-- Goals, compacted for reference -->
      {#if subject}
        <div class="goals-section bg-light p-3">
          <h3>
            Mål i <mark>{subject?.shortName || subject?.displayName}</mark>
            <ButtonIcon options={goalSectionToggleOptions} />
          </h3>
          {#if !localGoals}
            <p><em>Eleven har ingen mål i dette faget</em></p>
          {/if}

          {#if localGoals && isGoalSectionExpanded}
            <div class="d-flex flex-column gap-2 mt-2">
              {#each localGoals as goal}
                <div class="goal-row">
                  <span>{goal.sortOrder}</span>
                  {#if goal.isIndividual}
                    <span title="Individuelt mål">
                      <pkt-icon name="person"></pkt-icon>
                    </span>
                  {:else}
                    <span title="Gruppemål">
                      <pkt-icon name="group"></pkt-icon>
                    </span>
                  {/if}

                  {#if $dataStore.currentSchool.isGoalTitleEnabled}
                    <span class="goal-title">
                      {goal.title}
                    </span>
                  {/if}

                  <span class="goal-stats">
                    {#if goal.masteryData}
                      <MasteryLevelBadge
                        masteryData={goal.masteryData}
                        masterySchema={getMasterySchemaForGoal(goal)}
                      />
                      {#if $isMasteryBarChartVisible}
                        <MasteryBarChart
                          data={goal.observations?.map((o: ObservationType) => o.masteryValue)}
                          masterySchema={getMasterySchemaForGoal(goal)}
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

      <!-- Form fields -->
      <div class="mt-3">
        <!-- Kategori -->
        <div class="field-group">
          <label for="categorySelect" class="field-label">Kategori</label>
          <select
            class="form-control rounded-0 border-2 border-primary"
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

        <!-- Periode -->
        <div class="field-group">
          <span class="field-label">Periode</span>
          <div class="d-flex align-items-end gap-2 flex-wrap">
            <div class="flex-fill" style="min-width: 140px">
              <label for="beginAt" class="form-label small text-muted mb-1">Fra</label>
              <input
                id="beginAt"
                type="date"
                class="form-control rounded-0 border-2 border-primary"
                class:is-invalid={validationErrors.beginAt}
                bind:value={localStatus.beginAt}
                disabled={!!currentStatusCategory}
                required
              />
              {#if validationErrors.beginAt}
                <div class="text-danger small mt-1">{validationErrors.beginAt}</div>
              {/if}
            </div>
            <span class="text-muted pb-2">–</span>
            <div class="flex-fill" style="min-width: 140px">
              <label for="endAt" class="form-label small text-muted mb-1">Til</label>
              <input
                id="endAt"
                type="date"
                class="form-control rounded-0 border-2 border-primary"
                class:is-invalid={validationErrors.endAt}
                bind:value={localStatus.endAt}
                disabled={!!currentStatusCategory}
                required
              />
              {#if validationErrors.endAt}
                <div class="text-danger small mt-1">{validationErrors.endAt}</div>
              {/if}
            </div>
          </div>
        </div>

        <!-- Tittel -->
        <div class="field-group">
          <label for="title" class="field-label">Tittel</label>
          <div class="input-with-icon position-relative">
            <input
              id="title"
              type="text"
              class="form-control rounded-0 border-2 border-primary"
              bind:value={localStatus.title}
              placeholder="Angi en tittel"
              disabled={!!currentStatusCategory}
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

        <!-- Mestring -->
        {#if currentMasterySchema?.config?.isMasteryValueInputEnabled}
          <div class="field-group">
            <span class="field-label">Mestring</span>
            <MasteryValueInput
              masterySchema={currentMasterySchema}
              bind:value={localStatus.masteryValue}
            />
          </div>
        {/if}

        <!-- Beskrivelse -->
        {#if currentMasterySchema?.config?.isMasteryDescriptionInputEnabled}
          <div class="field-group">
            <label for="description" class="field-label">Beskrivelse</label>
            <textarea
              id="description"
              class="form-control rounded-0 border-2 border-primary"
              bind:value={localStatus.masteryDescription}
              placeholder="Kort beskrivelse av hva {studentFirstName} får til"
              rows="4"
            ></textarea>
          </div>
        {/if}

        <!-- Fremovermelding -->
        {#if currentMasterySchema?.config?.isFeedforwardInputEnabled}
          <div class="field-group">
            <label for="feedforward" class="field-label">Fremovermelding</label>
            <textarea
              id="feedforward"
              class="form-control rounded-0 border-2 border-primary"
              bind:value={localStatus.feedforward}
              placeholder="Konkret, hva kan {studentFirstName} gjøre for å forbedre seg?"
              rows="4"
            ></textarea>
          </div>
        {/if}
      </div>

      <!-- Actions -->
      <div class="d-flex gap-2 pt-4">
        <ButtonMini
          options={{
            title: 'Lagre',
            skin: 'primary',
            variant: 'label-only',
            size: 'medium',
            onClick: () => handleSave(),
          }}
        >
          Lagre
        </ButtonMini>

        <ButtonMini
          options={{
            title: 'Avbryt',
            skin: 'tertiary',
            variant: 'label-only',
            size: 'medium',
            onClick: () => onDone(),
          }}
        >
          Avbryt
        </ButtonMini>
      </div>
    </div>
  {:else}
    No status...
  {/if}
</div>

<style>
  .goals-section h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
    font-weight: 600;
  }

  .goal-row {
    display: grid;
    grid-template-columns: auto auto minmax(max-content, 30ch) 1fr;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    background-color: #fff;
    min-height: 2rem;
  }

  .goal-row > * {
    display: flex;
    align-items: center;
  }

  .goal-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .goal-stats {
    gap: 0.5rem;
  }

  .field-group {
    padding: 1rem 0;
    border-bottom: 1px solid var(--pkt-color-grays-gray-100, #e6e6e6);
  }

  .field-group:last-child {
    border-bottom: none;
  }

  .field-label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
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

  textarea {
    font-size: 1.2rem;
  }

  @media (max-width: 480px) {
    .goal-row {
      grid-template-columns: auto auto 1fr;
    }

    .goal-title {
      grid-column: 1 / -1;
    }
  }
</style>
