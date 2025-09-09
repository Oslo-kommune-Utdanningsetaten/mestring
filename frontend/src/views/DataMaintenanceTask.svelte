<script lang="ts">
  import { type DataMaintenanceTaskReadable } from '../generated/types.gen'
  import { dataMaintenanceTasksList } from '../generated/sdk.gen'

  let tasks = $state<DataMaintenanceTaskReadable[]>([])
  let loading = $state<boolean>(false)
  let errorMsg = $state<string | null>(null)

  const statusVariant: Record<string, string> = {
    pending: 'secondary',
    running: 'primary',
    finished: 'success',
    failed: 'danger',
  }

  const formatDate = (iso?: string | null) => {
    if (!iso) return ''
    try {
      // Keep it minimal: YYYY-MM-DD HH:MM
      const d = new Date(iso)
      if (Number.isNaN(d.getTime())) return ''
      return (
        d.toLocaleDateString('no-NO', { year: '2-digit', month: '2-digit', day: '2-digit' }) +
        ' ' +
        d.toLocaleTimeString('no-NO', { hour: '2-digit', minute: '2-digit' })
      )
    } catch {
      return ''
    }
  }

  const fetchTasks = async () => {
    loading = true
    errorMsg = null
    try {
      const result = await dataMaintenanceTasksList()
      tasks = (result.data || []).sort((a, b) => b.startedAt?.localeCompare(a.startedAt || '') || 0)
    } catch (error) {
      console.error('Error fetching tasks:', error)
      errorMsg = 'Kunne ikke hente bakgrunnsjobber'
      tasks = []
    } finally {
      loading = false
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
      <button class="btn btn-outline-secondary btn-sm" onclick={fetchTasks} disabled={loading}>
        {#if loading}<span class="spinner-border spinner-border-sm me-1" role="status"></span>{/if}
        Oppdater
      </button>
    </div>
  </div>

  {#if errorMsg}
    <div class="alert alert-danger py-2 px-3 mb-3">{errorMsg}</div>
  {/if}

  {#if loading && tasks.length === 0}
    <div class="alert alert-info py-2 px-3">Laster bakgrunnsjobber...</div>
  {:else if !loading && tasks.length === 0}
    <div class="alert alert-secondary py-2 px-3">Ingen jobber funnet.</div>
  {:else}
    <div class="table-responsive small">
      <table class="table table-sm table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>Status</th>
            <th>Visningsnavn</th>
            <th>Jobb</th>
            <th>Startet</th>
            <th>Ferdig</th>
            <th>Sist puls</th>
            <th>Forsøk</th>
            <th>Crash?</th>
            <th>Overwrite?</th>
          </tr>
        </thead>
        <tbody>
          {#each tasks as t}
            <tr class={t.status === 'failed' ? 'table-danger' : ''}>
              <td>
                <span
                  class={`badge text-bg-${statusVariant[t.status || 'pending'] || 'secondary'}`}
                >
                  {t.status}
                </span>
              </td>
              <td>{t.displayName || '-'}</td>
              <td class="text-muted">
                <code class="small">{t.jobName}</code>
              </td>
              <td>{formatDate(t.startedAt)}</td>
              <td>{formatDate(t.finishedAt || t.failedAt)}</td>
              <td>{formatDate(t.lastHeartbeatAt)}</td>
              <td>{t.attempts ?? 0}</td>
              <td>{t.isCrashOnErrorEnabled ? 'Ja' : 'Nei'}</td>
              <td>{t.isOverwriteEnabled ? 'Ja' : 'Nei'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</section>

<style>
</style>
