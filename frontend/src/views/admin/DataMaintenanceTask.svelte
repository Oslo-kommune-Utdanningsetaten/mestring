<script lang="ts">
  import { type DataMaintenanceTaskReadable } from '../../generated/types.gen'
  import { dataMaintenanceTasksList } from '../../generated/sdk.gen'

  let tasks = $state<DataMaintenanceTaskReadable[]>([])
  let isLoading = $state<boolean>(false)
  let openRows = $state<Record<string, boolean>>({})

  const statusVariant: Record<string, string> = {
    pending: 'secondary',
    running: 'primary',
    finished: 'success',
    failed: 'danger',
  }

  // YYYY-MM-DD HH:MM
  const formatDate = (isoDate?: string | null) => {
    if (!isoDate) return ''
    const d = new Date(isoDate)
    return (
      d.toLocaleDateString('no-NO', { year: '2-digit', month: '2-digit', day: '2-digit' }) +
      ' ' +
      d.toLocaleTimeString('no-NO', { hour: '2-digit', minute: '2-digit' })
    )
  }

  const handleRowClick = (taskId: string) => {
    openRows[taskId] = !openRows[taskId]
    openRows = { ...openRows }
  }

  const fetchTasks = async () => {
    isLoading = true
    try {
      const result = await dataMaintenanceTasksList()
      tasks = result.data || []
      tasks = tasks.sort((a, b) => {
        const dateA = new Date(a.createdAt || '').getTime() || 0
        const dateB = new Date(b.createdAt || '').getTime() || 0
        return dateB - dateA // Descending order
      })
    } catch (error) {
      console.error('Error fetching tasks:', error)
      tasks = []
    } finally {
      isLoading = false
    }
  }

  $effect(() => {
    fetchTasks()
  })
</script>

<section class="py-3">
  <div class="d-flex align-items-center justify-content-between mb-3 w-100">
    <h2 class="m-0">Bakgrunnsjobber</h2>
    <div class="d-flex gap-2">
      <button class="btn btn-outline-secondary btn-sm" onclick={fetchTasks} disabled={isLoading}>
        {#if isLoading}
          <span class="spinner-border spinner-border-sm me-1" role="status"></span>
        {:else}
          Oppdater
        {/if}
      </button>
    </div>
  </div>

  {#if isLoading}
    <div class="alert alert-info py-2 px-3">Laster bakgrunnsjobber...</div>
  {:else if !isLoading && tasks.length === 0}
    <div class="alert alert-secondary py-2 px-3">Ingen jobber funnet.</div>
  {:else}
    <div class="table-responsive small">
      <table class="table table-sm table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>status</th>
            <th>id</th>
            <th>display_name</th>
            <th>created_at</th>
            <th>attempts</th>
          </tr>
        </thead>
        <tbody>
          {#each tasks as task}
            <tr
              class={task.status === 'failed' ? 'table-danger' : ''}
              onclick={() => handleRowClick(task.id)}
            >
              <td>
                <span
                  class={`badge text-bg-${statusVariant[task.status || 'pending'] || 'secondary'}`}
                >
                  {task.status}
                </span>
              </td>
              <td>{task.id}</td>
              <td>{task.displayName || '-'}</td>
              <td>{formatDate(task.createdAt)}</td>
              <td>{task.attempts}</td>
            </tr>
            {#if openRows[task.id]}
              <tr>
                <td colspan="6"><pre>{JSON.stringify(task, null, 2)}</pre></td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</section>

<style>
</style>
