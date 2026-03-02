<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type DataMaintenanceTaskType } from '../../generated/types.gen'
  import { dataMaintenanceTasksList } from '../../generated/sdk.gen'
  import { formatDateTime } from '../../utils/functions'
  import { TASK_STATES } from '../../utils/constants'
  import Link from '../../components/Link.svelte'
  import ButtonMini from '../../components/ButtonMini.svelte'

  const router = useTinyRouter()

  let tasks = $state<DataMaintenanceTaskType[]>([])
  let isLoading = $state<boolean>(false)
  let openRows = $state<Record<string, boolean>>({})
  let backLink = $derived(router.getQueryParam('back') || null)

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
        const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0
        return dateB - dateA // Ascending order
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
  <div class="d-flex align-items-center mb-3 w-100">
    <h2 class="me-3">Bakgrunnsjobber</h2>
    <ButtonMini
      options={{
        title: 'Oppdater liste med bakgrunnsjobber',
        iconName: 'process-forward',
        skin: 'secondary',
        variant: 'icon-left',
        onClick: () => fetchTasks(),
      }}
    >
      Oppdater
    </ButtonMini>
  </div>
  <div class="my-3">
    {#if backLink}
      <Link to={backLink}>Tilbake til skolen</Link>
    {/if}
  </div>

  {#if isLoading}
    <div class="alert alert-info py-2 px-3">Laster bakgrunnsjobber...</div>
  {:else if !isLoading && tasks.length === 0}
    <div class="alert alert-secondary py-2 px-3">Ingen jobber funnet.</div>
  {:else}
    <div class="table-responsive small">
      <table class="table table-sm table-hover table-striped align-middle mb-0">
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
                  class={`badge text-bg-${TASK_STATES[task.status || 'pending'] || 'secondary'}`}
                >
                  {task.status}
                </span>
              </td>
              <td>{task.id}</td>
              <td>{task.displayName || '-'}</td>
              <td>
                <span class="timestamp">{formatDateTime(task.createdAt)?.split(' ')[0]}</span>
                <span class="timestamp">{formatDateTime(task.createdAt)?.split(' ')[1]}</span>
              </td>
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
  .timestamp {
    background-color: var(--pkt-color-grays-gray-200);
    padding: 0.05rem 0.2rem;
  }
</style>
