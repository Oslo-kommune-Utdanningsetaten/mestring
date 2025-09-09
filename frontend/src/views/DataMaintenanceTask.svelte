<script lang="ts">
  import { type DataMaintenanceTaskReadable } from '../generated/types.gen'
  import { dataMaintenanceTasksList } from '../generated/sdk.gen'
  import { setCurrentSchool } from '../stores/data'

  let tasks = $state<DataMaintenanceTaskReadable[]>([])

  const fetchTasks = async () => {
    try {
      const result = await dataMaintenanceTasksList()
      tasks = result.data || []
    } catch (error) {
      console.error('Error fetching tasks:', error)
      tasks = []
    }
  }

  $effect(() => {
    fetchTasks()
  })
</script>

<section class="py-3">
  <h2>Bakgrunnsjobber</h2>

  <!-- Schools list -->
  <div class="d-flex flex-column align-items-start gap-2 w-100">
    {#if tasks.length === 0}
      <div class="alert alert-info">Laster bakgrunnsjobber...</div>
    {:else}
      hello
    {/if}
  </div>
</section>

<style>
</style>
