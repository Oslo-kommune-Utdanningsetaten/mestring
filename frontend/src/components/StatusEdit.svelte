<script lang="ts">
  import type {
    StatusType,
    SubjectType,
    UserType,
    ObservationType,
    GoalType,
  } from '../generated/types.gen'
  import { statusCreate, statusUpdate } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparkbarChart from './SparkbarChart.svelte'

  import type { GoalDecorated } from '../types/models'

  const { status, student, subject, goals, onDone } = $props<{
    status: StatusType | {} | null
    student: UserType | null
    subject: SubjectType | null
    goals: GoalDecorated[]
    onDone: () => void
  }>()

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

  // Update localStatus when status prop changes
  $effect(() => {
    localStatus = {
      ...status,
    }
  })
</script>

<div class="status-edit p-4">
  {#if localStatus}
    <!-- Name and subject -->
    <h2 class="my-4">
      <mark>{student?.name}</mark>
      i faget
      <mark>{subject.shortName || subject.displayName}</mark>
    </h2>

    <!-- Goals, compacted for reference -->
    <div class="my-4">
      <h4>Elevens mål i faget</h4>
      {#if goals.length > 0}
        <div class="goals-container mt-2">
          {#each goals as goal}
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
                {/if}
              </span>
            </div>
          {/each}
        </div>
      {:else}
        <p><em>Ingen mål for denne eleven i dette faget</em></p>
      {/if}
    </div>

    <h2 class="my-4">
      {localStatus.id ? 'Redigerer' : 'Opprett ny'} status
    </h2>

    <!-- Begin and end dates -->
    <div class="row my-4">
      <div class="col-auto form-group">
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
      <div class="col-auto form-group">
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

    <!-- Mastery value input -->
    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      <div class="my-4">
        {#if renderDirection() === 'vertical'}
          <ValueInputVertical
            {masterySchema}
            bind:masteryValue={localStatus.masteryValue}
            label="Mestring i denne perioden"
          />
        {:else}
          <ValueInputHorizontal
            {masterySchema}
            bind:masteryValue={localStatus.masteryValue}
            label="Mestring i denne perioden"
          />
        {/if}
      </div>
    {/if}

    <!-- Mastery description input -->
    {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="form-group my-4">
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
      <div class="form-group my-4">
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

    <div class="d-flex gap-2 justify-content-start mt-4">
      <ButtonMini
        options={{
          title: 'Lagre',
          iconName: 'check',
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
          iconName: 'close',
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
    background-color: var(--pkt-color-brand-neutrals-200);
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
