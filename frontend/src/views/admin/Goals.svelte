<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GoalType } from '../../generated/types.gen'
  import { goalsList } from '../../generated/sdk.gen'
  import { formatDateTime } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import { addAlert } from '../../stores/alerts'
  import { dataStore } from '../../stores/data'
  import Link from '../../components/Link.svelte'

  const router = useTinyRouter()
  let goals = $state<GoalType[]>([])

  const fetchGoals = async () => {
    try {
      const currentSchoolId = $dataStore.currentSchool?.id
      const result = await goalsList({ query: { school: currentSchoolId } })

      goals = result.data || []
      // .sort((a, b) => a.displayName.localeCompare(b.displayName, 'nb', { sensitivity: 'base' }))
      // .sort((a, b) => Number(!a.isServiceEnabled) - Number(!b.isServiceEnabled))
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av mål',
      })
      goals = []
    }
  }

  $effect(() => {
    fetchGoals()
  })
</script>

<section class="container py-3">
  <h2>Alle mål ved skolen</h2>

  {#each goals as goal}
    <!-- A tight table listing of goals, along with the name of whow created it and an icon indicating individual or group -->
    <div class="card shadow-sm p-3 mb-2">
      <h3 class="mt-1 mb-3" title={goal.id}>
        <Link to="/admin/goals/{goal.id}">
          {goal.title}
        </Link>
      </h3>
      <div class="d-flex justify-content-between align-items-center">
        <div>
          Opprettet av: {goal.createdById}
        </div>
        <div>
          {formatDateTime(goal.createdAt)}
        </div>
      </div>
    </div>
  {/each}
</section>

<style>
</style>
