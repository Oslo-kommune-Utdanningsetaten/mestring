<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import { observationsList } from '../generated/sdk.gen'
  import ButtonMini from './ButtonMini.svelte'
  import MasteryValueInput from './MasteryValueInput.svelte'
  import AuthorInfo from './AuthorInfo.svelte'

  let { currentSchool, currentUser } = $derived($dataStore)

  let observationsByMe = $state<ObservationType[]>([])
  let observationsOfMe = $state<ObservationType[]>([])
  let observations = $derived(
    [...observationsByMe, ...observationsOfMe].sort(
      (a: ObservationType, b: ObservationType) =>
        new Date(b?.observedAt).getTime() - new Date(a?.observedAt).getTime()
    )
  )

  // TODO: Fetch both observered by me and where I'm as student (possibly merge, if same). Then render in two different lists ''

  const fetchObservations = async () => {
    try {
      const [obmResult, oomResult] = await Promise.all([
        observationsList({
          query: { observer: currentUser?.id, school: currentSchool?.id },
        }),
        observationsList({
          query: { student: currentUser?.id, school: currentSchool?.id },
        }),
      ])
      observationsByMe = obmResult.data || []
      observationsOfMe = oomResult.data || []
    } catch (error) {
      console.error('Error fetching observations:', error)
    }
  }

  $effect(() => {
    fetchObservations()
  })
</script>

<section class="py-4">
  <h2>Observasjoner</h2>

  {#if observationsByMe.length + observationsOfMe.length === 0}
    <div class="mt-3">🫤 Her var det lite, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4">
      {#each observations as observation, i}
        <span>
          <AuthorInfo item={observation} />
          {observation.studentId} --> {observation.masteryValue}
          ()
        </span>
      {/each}
    </div>
  {/if}
</section>

<style>
  .group-row {
    display: grid;
    grid-template-columns: 25rem 12rem auto auto;
    align-items: center;
    gap: 20px;
  }

  .group-name {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }
</style>
