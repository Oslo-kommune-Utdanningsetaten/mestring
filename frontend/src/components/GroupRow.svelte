<script lang="ts">
  import type { Mastery } from '../types/models'
  import type {
    GroupType,
    SubjectType,
    ObservationType,
    MasterySchemaType,
  } from '../generated/types.gen'
  import { inferMastery } from '../utils/functions'
  import { dataStore } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import { goalsRetrieve } from '../generated/sdk.gen'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import MasteryBarChart from './MasteryBarChart.svelte'
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

  $effect(() => {
    if (observations?.length > 0) {
      inferMasterySchema()
    }
  })
</script>

{#if group}
  <span class="item group-name">
    <Link to={`/groups/${group.id}`}>{group.displayName}</Link>
  </span>
  {#each subjects as subject}
    <span class="item">
      {#if subject && observationsBySubjectId[subject.id]?.length}
        <span class="me-1" title={subject.displayName}>
          <MasteryLevelBadge
            masteryData={inferMastery(observationsBySubjectId[subject.id]) ?? undefined}
            masterySchema={assumedMasterySchema}
            isLastValueVisible={false}
          />
        </span>

        {#if $isMasteryBarChartVisible}
          <MasteryBarChart
            data={observationsBySubjectId[subject.id].map(
              (obs: ObservationType) => obs.masteryValue ?? 0
            )}
            masterySchema={assumedMasterySchema}
          />
        {/if}
      {:else}
        <span class="text-muted">---</span>
      {/if}
    </span>
  {/each}
{/if}

<style>
</style>
