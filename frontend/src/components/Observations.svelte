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

  let observations = $state<ObservationType[]>([])

  const fetchObservations = async () => {
    try {
      const result = await observationsList({
        query: { student: currentUser?.id, school: currentSchool?.id },
      })
      console.log('Fetched observations:', result.data)
      observations = result.data || []
    } catch (error) {
      console.error('Error fetching observations:', error)
    }
  }

  $effect(() => {
    fetchObservations()
  })
</script>

<section class="py-3">
  <h2>Observasjoner</h2>

  {#if observations.length === 0}
    <div class="mt-3">🫤 Her var det lite, gitt.</div>
  {:else}
    <div class="card shadow-sm">
      {#each observations as observation, i}
        <pre>{JSON.stringify(observation, null, 2)}</pre>
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
