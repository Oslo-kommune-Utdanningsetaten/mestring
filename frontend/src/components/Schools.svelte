<script lang="ts">
  import { type SchoolReadable } from '../api/types.gen'
  import { schoolsList, schoolsPartialUpdate } from '../api/sdk.gen'

  let schools = $state<SchoolReadable[]>([])

  async function fetchSchools() {
    try {
      const result = await schoolsList()
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  async function toggleServiceEnabled(school: SchoolReadable) {
    try {
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isServiceEnabled: !school.isServiceEnabled },
      })
      // Update local school
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating school:', error)
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="py-3">
  <h2>Skoler</h2>

  <!-- Schools list -->
  <div class="d-flex flex-column align-items-start gap-2 w-100">
    {#if schools.length === 0}
      <div class="alert alert-info">Laster skoler...</div>
    {:else}
      <ul class="list-group w-100">
        {#each schools as school}
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              {school.displayName}
            </div>

            <div class="form-check form-switch">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                checked={school.isServiceEnabled}
                onchange={() => toggleServiceEnabled(school)}
              />
              <label class="form-check-label" for="serviceSwitch-{school.id}">
                {school.isServiceEnabled ? 'Aktiv' : 'Inaktiv'}
              </label>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</section>

<style>
  .form-check-input {
    cursor: pointer;
  }

  /* Larger switch size */
  .form-switch .form-check-input {
    width: 3em;
    height: 1.5em;
    margin-right: 0.5em;
  }
</style>
