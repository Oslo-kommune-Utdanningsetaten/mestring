<script lang="ts">
  import { type SchoolReadable } from '../generated/types.gen'
  import { schoolsList, schoolsPartialUpdate } from '../generated/sdk.gen'
  import { setCurrentSchool } from '../stores/data'

  let schools = $state<SchoolReadable[]>([])
  let importingSchool = $state<Set<number>>(new Set())
  let alertMessage = $state<string>('')
  let alertType = $state<'success' | 'error' | ''>('')
  let showDetails = $state<boolean>(false)
  let rawJsonResult = $state<any>(null)
  let fetchingGroups = $state<boolean>(false)
  let imporingSchools = $state<boolean>(false)
  let dryRun = $state(false)
  let overwrite = $state(false)
  let crashOnError = $state(false)

  const fetchSchools = async () => {
    try {
      const result = await schoolsList()
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const toggleServiceEnabled = async (school: SchoolReadable) => {
    try {
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isServiceEnabled: !school.isServiceEnabled },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating school:', error)
    }
  }

  const dismissAlert = () => {
    alertMessage = ''
    alertType = ''
    showDetails = false
    rawJsonResult = null
  }

  const syncSchoolData = async (school: SchoolReadable) => {
    importingSchool = new Set([...importingSchool, school.id])
    dismissAlert()
    try {
      const response = await fetch(`/api/import/school/${school.orgNumber}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_dryrun_enabled: dryRun,
          is_overwrite_enabled: overwrite,
          is_crash_on_error_enabled: crashOnError,
        }),
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        const taskId = result.task?.id || ''
        alertMessage =
          `✅ Import fullført for ${school.displayName}!` + (taskId ? ` (Task: ${taskId})` : '')
        alertType = 'success'
        rawJsonResult = result.task?.result || null
        await fetchSchools()
      } else {
        alertMessage = `❌ Import feilet for ${school.displayName}: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Import feilet for ${school.displayName}: ${e?.message || 'Nettverksfeil'}`
      alertType = 'error'
    } finally {
      importingSchool = new Set([...importingSchool].filter(id => String(id) !== String(school.id)))
    }
  }

  const fetchGroups = async () => {
    dismissAlert()
    fetchingGroups = true
    try {
      const response = await fetch('/api/fetch/groups/', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        alertMessage = '✅ Grupper hentet fra Feide!'
        alertType = 'success'
        rawJsonResult = result.step_results || null
      } else {
        alertMessage = `❌ Feil ved henting av grupper: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    } finally {
      fetchingGroups = false
    }
  }

  const importSchoolsApi = async () => {
    dismissAlert()
    imporingSchools = true
    try {
      const response = await fetch('/api/import/schools/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_dryrun_enabled: dryRun,
          is_overwrite_enabled: overwrite,
          is_crash_on_error_enabled: crashOnError,
        }),
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        alertMessage = '✅ Skoler importert fra fil!'
        alertType = 'success'
        rawJsonResult = result.step_results || null
        await fetchSchools()
      } else {
        alertMessage = `❌ Feil ved import av skoler: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    } finally {
      imporingSchools = false
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="py-3">
  <h2>Skoler</h2>
  <button class="btn btn-primary mb-3" onclick={fetchGroups}>
    {#if fetchingGroups}
      <span class="spinner-border spinner-border-sm me-2"></span>
      Henter grupper..... tar litt tid
    {:else}
      Hent grupper fra feide
    {/if}
  </button>

  <button class="btn btn-primary mb-3" onclick={importSchoolsApi}>
    {#if imporingSchools}
      <span class="spinner-border spinner-border-sm me-2"></span>
      Importerer skoler fra fil...
    {:else}
      Importer skoler fra fil
    {/if}
  </button>

  <div class="d-flex align-items-center gap-3 mb-3">
  <div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" bind:checked={dryRun} id="dryRunSwitch" />
    <label class="form-check-label" for="dryRunSwitch">Dry-run (ingen DB-skriving)</label>
  </div>
  <div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" bind:checked={overwrite} id="overwriteSwitch" />
    <label class="form-check-label" for="overwriteSwitch">Overwrite eksisterende</label>
  </div>
  <div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" bind:checked={crashOnError} id="crashSwitch" />
    <label class="form-check-label" for="crashSwitch">Stopp ved feil</label>
  </div>
</div>

  {#if alertMessage}
    <div
      class="alert alert-{alertType === 'success' ? 'success' : 'danger'} alert-dismissible"
      role="alert"
    >
      <div class="d-flex justify-content-between align-items-start">
        <div class="flex-grow-1">
          {alertMessage}

          {#if rawJsonResult && alertType === 'success'}
            <div class="mt-2">
              <button
                class="btn btn-sm btn-outline-secondary"
                onclick={() => (showDetails = !showDetails)}
              >
                {showDetails ? '📄 Skjul JSON' : '📋 Vis JSON resultat'}
              </button>
            </div>

            {#if showDetails}
              <div class="mt-3 p-3 bg-light rounded">
                <h6>Raw JSON fra database:</h6>
                <pre
                  class="bg-white p-2 border rounded small overflow-auto"
                  style="max-height: 400px;">
                    {JSON.stringify(rawJsonResult, null, 2)}
                </pre>
              </div>
            {/if}
          {/if}
        </div>

        <button type="button" class="btn-close" onclick={dismissAlert}></button>
      </div>
    </div>
  {/if}

  <div class="d-flex flex-column gap-2 w-100">
    {#if schools.length === 0}
      <div class="alert alert-info">Laster skoler...</div>
    {:else}
      {#each schools as school}
        <div class="card">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div class="school-info">
              {#if school.isServiceEnabled}
                <a href="/" onclick={() => setCurrentSchool(school)} class="text-decoration-none">
                  <h6 class="mb-1">{school.displayName}</h6>
                  <small class="text-muted">
                    {school.orgNumber} • Sist oppdatert: {new Date(school.updatedAt).toLocaleString(
                      'nb-NO'
                    )}
                  </small>
                </a>
              {:else}
                <h6 class="mb-1 text-muted">{school.displayName}</h6>
                <small class="text-muted">
                  {school.orgNumber} • Sist oppdatert: {new Date(school.updatedAt).toLocaleString(
                    'nb-NO'
                  )}
                </small>
              {/if}
            </div>

            <div class="d-flex align-items-center gap-2">
              <button
                class="btn btn-outline-primary btn-sm"
                onclick={() => syncSchoolData(school)}
                disabled={importingSchool.has(school.id)}
              >
                {#if importingSchool.has(school.id)}
                  <span class="spinner-border spinner-border-sm me-1"></span>
                  Importerer...
                {:else}
                  📥 Importer
                {/if}
              </button>

              <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  checked={school.isServiceEnabled}
                  onchange={() => toggleServiceEnabled(school)}
                />
                <label class="form-check-label">
                  {school.isServiceEnabled ? 'Aktiv' : 'Inaktiv'}
                </label>
              </div>
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</section>

<style>
  .card {
    transition: box-shadow 0.2s ease;
  }

  .card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .spinner-border-sm {
    width: 0.8rem;
    height: 0.8rem;
  }

  .bg-light {
    background-color: #f8f9fa !important;
  }

</style>
