<script lang="ts">
  import type {
    GroupType,
    SubjectType,
    ObservationType,
    MasterySchemaType,
  } from '../generated/types.gen'
  import type { MasteryData } from '../types/models'

  import { inferMastery } from '../utils/functions'
  import { dataStore } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import { goalsRetrieve } from '../generated/sdk.gen'
  import { useMasteryCalculations } from '../utils/masteryHelpers'

  import MasteryBarChart from './MasteryBarChart.svelte'
  import SubjectTrendBarChart from './SubjectTrendBarChart.svelte'
  import Link from './Link.svelte'

  let {
    group,
    subjects,
    observations,
  }: {
    group: GroupType
    subjects: SubjectType[]
    observations: ObservationType[]
  } = $props()

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')

  let assumedMasterySchema = $state<MasterySchemaType>()
  let calculations = $derived(useMasteryCalculations(assumedMasterySchema))

  const observationsBySubjectId = $derived.by(() => {
    const result: Record<string, ObservationType[]> = {}
    observations.forEach((obs: ObservationType) => {
      const subjectId = obs.subjectId as string
      result[subjectId] = result[subjectId] || []
      result[subjectId].push(obs)
    })
    // sort observations for each subject by observedAt date, oldest first
    Object.keys(result).forEach(subjectId => {
      result[subjectId] = (result[subjectId] as ObservationType[]).sort(
        (a: ObservationType, b: ObservationType) =>
          new Date(a.observedAt ?? 0).getTime() - new Date(b.observedAt ?? 0).getTime()
      )
    })
    return result
  })

  // First pass: Nested by subjectId, then studentId, then goalId, wherein we have arrays of observations
  const observationsBySubjectIdAndStudentIdAndGoalId: Record<
    string,
    Record<string, Record<string, ObservationType[]>>
  > = $derived.by(() => {
    const result: Record<string, Record<string, Record<string, ObservationType[]>>> = {}
    observations.forEach((observation: ObservationType) => {
      const { subjectId, studentId, goalId } = observation
      if (!subjectId || !studentId || !goalId) return
      if (!result[subjectId]) {
        result[subjectId] = {}
      }
      if (!result[subjectId][studentId]) {
        result[subjectId][studentId] = {}
      }
      if (!result[subjectId][studentId][goalId]) {
        result[subjectId][studentId][goalId] = []
      }
      result[subjectId][studentId][goalId].push(observation)
    })
    return result
  })

  // Next pass: Infer mastery for observations within each subject, student and goal
  // Then aggregate masteries by subject, so we have arrays of mastery objects for each subject, which we can use to render the trend bars
  const masteriesBySubjectId: Record<string, MasteryData[]> = $derived.by(() => {
    const result: Record<string, MasteryData[]> = {}
    Object.entries(observationsBySubjectIdAndStudentIdAndGoalId).forEach(
      ([subjectId, observationsByStudentIdAndGoalId]) => {
        const masteriesForSubject: MasteryData[] = []
        Object.values(observationsByStudentIdAndGoalId).forEach(observationsByGoalId => {
          Object.values(observationsByGoalId).forEach(observationsForGoal => {
            const mastery = inferMastery(observationsForGoal)
            if (mastery) {
              masteriesForSubject.push(mastery)
            }
          })
        })
        result[subjectId] = masteriesForSubject
      }
    )
    return result
  })

  const inferMasterySchema = async () => {
    // We're assuming that all observations within a group use the same mastery schema
    const someGoalId = observations.find(obs => obs.goalId)?.goalId
    if (!someGoalId) {
      console.warn(
        'No goal found in observations, cannot infer mastery schema from group',
        group.id
      )
      return
    }
    const goalResult = await goalsRetrieve({
      path: { id: someGoalId },
    })
    const goal = goalResult.data
    if (!goal) {
      console.warn('Goal not found, cannot infer mastery schema from group', {
        someGoalId,
        groupId: group.id,
      })
      return
    }
    assumedMasterySchema = $dataStore.masterySchemas.find(
      schema => schema.id === goal.masterySchemaId
    )
  }

  // Takes a list of mastery objects and returns an array containing the count of decreasing, flat and inreasing values
  const calculateTrendRepresentation = (masteries: MasteryData[]): [number, number, number] => {
    let decreasing = 0
    let flat = 0
    let inreasing = 0
    masteries.forEach(mastery => {
      const trend = mastery.trend
      const isFlat = Math.abs(trend) < calculations.flatTrendThreshold
      const isDecreasing = trend < 0 && !isFlat
      if (isDecreasing) {
        decreasing++
      } else if (isFlat) {
        flat++
      } else {
        inreasing++
      }
    })
    return [decreasing, flat, inreasing]
  }

  $effect(() => {
    if (observations?.length > 0) {
      inferMasterySchema()
    }
  })
</script>

{#if group}
  <span class="item group-name">
    <Link to={`/groups/${group.id}`}>{group.displayName}</Link>
    {#if !assumedMasterySchema}
      <span class="ms-2 text-muted fs-6">[mangler data 🫤]</span>
    {/if}
  </span>
  {#each subjects as subject}
    <span class="item gap-2">
      {#if subject && observationsBySubjectId[subject.id]?.length}
        <SubjectTrendBarChart
          data={calculateTrendRepresentation(masteriesBySubjectId[subject.id])}
          width={50}
          height={30}
          yResolution={calculations.inputValueIncrement}
        />

        {#if $isMasteryBarChartVisible && assumedMasterySchema}
          <MasteryBarChart
            data={observationsBySubjectId[subject.id].map(
              (obs: ObservationType) => obs.masteryValue ?? 0
            )}
            masterySchema={assumedMasterySchema}
          />
        {/if}
      {:else}
        <span class="text-muted fs-6"></span>
      {/if}
    </span>
  {/each}
{/if}

<style>
</style>
