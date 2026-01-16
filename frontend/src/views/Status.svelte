<script lang="ts">
  import type { StatusType, SubjectType, UserType, GoalType } from '../generated/types.gen'
  import { statusRetrieve, usersRetrieve, subjectsRetrieve } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import { fetchGoalsForSubjectAndStudent } from '../utils/functions'
  import type { GoalDecorated } from '../types/models'

  let { statusId } = $props<{
    statusId: string
  }>()

  let status = $state<StatusType | null>(null)
  let student = $state<UserType | null>(null)
  let subject = $state<SubjectType | null>(null)
  let goals = $state<GoalDecorated[] | null>(null)
  let isLoading = $state<boolean>(true)
  let isGoalSectionExpanded = $state<boolean>(false)

  const goalSectionToggleOptions = $derived.by(() => {
    return {
      iconName: `chevron-thin-${isGoalSectionExpanded ? 'up' : 'down'}`,
      title: `${isGoalSectionExpanded ? 'Skjul' : 'Vis'} mål`,
      onClick: () => toggleGoalsExpansion(),
    }
  })

  const masterySchema: MasterySchemaWithConfig = $derived(
    $dataStore.masterySchemas.find(ms => ms.id === status?.masterySchemaId) ||
      $dataStore.defaultMasterySchema
  )

  const calculations = $derived(useMasteryCalculations(masterySchema))

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const toggleGoalsExpansion = () => {
    isGoalSectionExpanded = !isGoalSectionExpanded
  }

  const fetchData = async () => {
    isLoading = true
    try {
      // Fetch status
      const statusResult = await statusRetrieve({ path: { id: statusId } })
      status = statusResult.data!

      if (!status) {
        isLoading = false
        return
      }

      // Fetch student
      const studentResult = await usersRetrieve({ path: { id: status.studentId } })
      student = studentResult.data!

      // Fetch subject
      const subjectResult = await subjectsRetrieve({ path: { id: status.subjectId } })
      subject = subjectResult.data!

      // Fetch goals
      if (student && subject) {
        goals = await fetchGoalsForSubjectAndStudent(
          subject.id,
          student.id,
          $dataStore.currentUser.allGroups
        )
      }
    } catch (error) {
      console.error('Error fetching status data:', error)
    } finally {
      isLoading = false
    }
  }

  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('nb-NO', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  $effect(() => {
    if (statusId) {
      fetchData()
    }
  })
</script>

<section>
  {#if isLoading}
    <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Laster...</span>
      </div>
    </div>
  {:else if status && subject && student}
    <!-- Name and subject -->
    <h2 class="my-3">
      Status for
      <mark>{student.name}</mark>
      i faget
      <mark>{subject.shortName || subject.displayName}</mark>
      , {status.title}
    </h2>

    <hr />

    <!-- Begin and end dates -->
    <div class="row my-4">
      <h3 class="col-2">Periode</h3>
      <div class="col-10">
        <p class="mb-0">
          {formatDate(status.beginAt)} – {formatDate(status.endAt)}
        </p>
      </div>
    </div>

    <hr />

    <!-- Mastery value display -->
    {#if masterySchema?.config?.isMasteryValueInputEnabled && status.masteryValue !== null && status.masteryValue !== undefined}
      <div class="row my-4">
        <h3 class="col-2">Mestring</h3>
        <div class="ps-2 col-10">
          <div
            class="mastery-scale"
            class:mastery-scale-horizontal={masterySchema?.config?.renderDirection === 'horizontal'}
            class:mastery-scale-vertical={masterySchema?.config?.renderDirection === 'vertical'}
          >
            {#each calculations.masteryLevels as level}
              <div
                class="mastery-level"
                class:active={status.masteryValue >= level.minValue &&
                  status.masteryValue <= level.maxValue}
                style="--level-color: {level.color}; background-color: var(--level-color);"
              >
                <strong>{level.title}</strong>
              </div>
            {/each}
          </div>
          <p class="mt-2">
            {status.masteryValue}
          </p>
        </div>
      </div>
    {/if}

    <!-- Mastery description display -->
    {#if masterySchema?.config?.isFeedforwardInputEnabled && status.masteryDescription}
      <div class="row my-4">
        <h3 class="col-2">Beskrivelse</h3>
        <div class="ps-2 col-10">
          {status.masteryDescription}
        </div>
      </div>
    {/if}

    <!-- Mastery feed forward display -->
    {#if masterySchema?.config?.isFeedforwardInputEnabled && status.feedforward}
      <div class="row my-4">
        <h3 class="col-2">Fremovermelding</h3>
        <div class="ps-2 col-10">
          {status.feedforward}
        </div>
      </div>
    {/if}
  {:else}
    <p>Status ikke funnet</p>
  {/if}
</section>

<style>
  .mastery-scale {
    display: flex;
    gap: 0.5rem;
  }

  .mastery-scale-vertical {
    flex-direction: column;
  }

  .mastery-scale-horizontal {
    flex-direction: row;
  }

  .mastery-level {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
  }

  .mastery-scale-horizontal .mastery-level {
    flex: 1;
    text-align: center;
  }

  .mastery-level.active {
    border-color: color-mix(in srgb, var(--level-color) 70%, black);
    border-width: 10px;
    border-style: outset;
    font-weight: 600;
  }
</style>
