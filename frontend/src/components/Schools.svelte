<script lang="ts">
  import { type SchoolReadable } from '../api/types.gen'
  import client from '../utils/httpClient'
  import { schoolsList } from '../api/sdk.gen'

  let schools: SchoolReadable[] = $state([])

  async function fetchSchools() {
    try {
      const result = await schoolsList()
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="py-3">
  <h2>Skoler</h2>

  <!-- Schools list -->
  <div class="d-flex align-items-center gap-2">
    {#if schools.length === 0}
      <div class="alert alert-info">Laster skoler...</div>
    {:else}
      <ul class="list-group">
        {#each schools as school}
          <li class="list-group-item">
            {school.displayName}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</section>

<style>
</style>
