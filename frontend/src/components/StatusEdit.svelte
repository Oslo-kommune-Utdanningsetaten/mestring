<script lang="ts">
  import { onMount } from 'svelte'
  import type {
    StatusType,
    SubjectType,
    UserType,
    ObservationType,
    GoalType,
  } from '../generated/types.gen'
  import { statusCreate, statusUpdate, usersRetrieve } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparkbarChart from './SparkbarChart.svelte'
  import { fetchGoalsForSubjectAndStudent, formatMonthName } from '../utils/functions'
  import type { GoalDecorated } from '../types/models'

  let { status, student, subject, goals, onDone } = $props<{
    status: StatusType | {} | null
    subject: SubjectType | null
    student?: UserType | null
    goals?: GoalDecorated[]
    onDone: () => void
  }>()

  let localStudent = $state<UserType | null>(student || null)
  let localGoals = $state<GoalDecorated[] | null>(goals || null)

  let isGoalSectionExpanded = $state<boolean>(false)

  const goalSectionToggleOptions = $derived.by(() => {
    return {
      iconName: `chevron-thin-${isGoalSectionExpanded ? 'up' : 'down'}`,
      title: `${isGoalSectionExpanded ? 'Skjul' : 'Vis'} mål`,
      onClick: () => toggleGoalsExpansion(),
    }
  })

  const masterySchema: MasterySchemaWithConfig = $derived($dataStore.defaultMasterySchema)
  const calculations = $derived(useMasteryCalculations(masterySchema))

  let localStatus = $state<Partial<StatusType> & { masteryValue: number }>({
    masteryValue: calculations.defaultValue,
  })

  let validationErrors = $state<{ beginAt?: string; endAt?: string }>({})

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const renderDirection = (): 'horizontal' | 'vertical' | 'unknown' => {
    return masterySchema?.config?.renderDirection || 'unknown'
  }

  const fetchStudentData = async () => {
    const userResult = await usersRetrieve({ path: { id: status.studentId } })
    localStudent = userResult.data!
    if (!localStudent) return
    localGoals = await fetchGoalsForSubjectAndStudent(
      subject.id,
      localStudent.id,
      $dataStore.currentUser.allGroups
    )
  }

  const handleGenerateTitle = () => {
    localStatus = {
      ...localStatus,
      title: `${formatMonthName(localStatus.beginAt)} - ${formatMonthName(localStatus.endAt)}`,
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

    localStatus.studentId = student?.id
    localStatus.subjectId = subject?.id
    localStatus.schoolId = $dataStore.currentSchool?.id
    try {
      if (localStatus.id) {
        const result = await statusUpdate({
          path: { id: localStatus.id },
          body: localStatus as any,
        })
      } else {
        const result = await statusCreate({
          body: localStatus as any,
        })
      }
      onDone()
    } catch (error) {
      console.error('Error saving status:', error)
    }
  }

  onMount(() => {
    localStatus = {
      ...status,
    }
  })

  $effect(() => {
    if (!student) {
      fetchStudentData()
    }
  })
</script>

<div class="status-edit p-4">
  {#if localStatus && subject && localStudent}
    <!-- Name and subject -->
    <h2 class="mt-3 mb-5">
      <mark>{localStudent.name}</mark>
      i faget
      <mark>{subject.shortName || subject.displayName}</mark>
    </h2>

    <!-- Goals, compacted for reference -->
    <div class="my-5 goals-section">
      <h4>
        Elevens mål i faget <ButtonIcon options={goalSectionToggleOptions} />
      </h4>
      {#if !localGoals}
        <p><em>Ingen mål for denne eleven i dette faget</em></p>
      {/if}
      {#if localGoals && isGoalSectionExpanded}
        <div class="goals-container mt-2">
          {#each localGoals as goal}
            <div class="goal-row">
              <span class="goal-sort-order">{goal.sortOrder}</span>

              {#if goal.isPersonal}
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
                  <SparkbarChart
                    data={goal.observations?.map((o: ObservationType) => o.masteryValue)}
                    masterySchema={getMasterySchmemaForGoal(goal)}
                  />
                {:else}
                  Ingen observasjoner i dette målet
                {/if}
              </span>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <h2 class="my-4">
      {localStatus.id ? 'Redigerer' : 'Opprett ny'} status
    </h2>

    <!-- Begin and end dates -->
    <div class="row my-5">
      <h3 class="col-2">Periode</h3>
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
      <div class="col-auto">
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
    <div class="row my-5">
      <h3 class="col-2">Tittel</h3>
      <div class="col-10">
        <div class="input-with-icon">
          <input
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
    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      <div class="row my-5">
        <h3 class="col-2">Mestring</h3>
        <div class="col-10">
          {#if renderDirection() === 'vertical'}
            <ValueInputVertical
              {masterySchema}
              bind:masteryValue={localStatus.masteryValue}
              label="Totalt sett, i denne perioden"
            />
          {:else}
            <ValueInputHorizontal
              {masterySchema}
              bind:masteryValue={localStatus.masteryValue}
              label="Totalt sett, i denne perioden"
            />
          {/if}
        </div>
      </div>
    {/if}

    <!-- Mastery description input -->
    {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="my-4">
        <label for="description" class="form-label">Beskrivelse/tilbakemelding</label>
        <textarea
          id="description"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localStatus.masteryDescription}
          placeholder="Kort beskrivelse av elevens mestringsnivå"
          rows="4"
        ></textarea>
      </div>
    {/if}

    <!-- Mastery feed forward input -->
    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="my-4">
        <label for="feedforward" class="form-label">Fremovermelding</label>
        <textarea
          id="feedforward"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localStatus.feedforward}
          placeholder="Konkret, hva kan eleven gjøre for å forbedre seg?"
          rows="4"
        ></textarea>
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

  .input-with-icon :global(button) {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
  }

  .goals-section {
    background-color: var(--pkt-color-brand-neutrals-200);
    padding: 0.5rem;

    h4 {
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
