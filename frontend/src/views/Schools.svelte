<script lang="ts">
  import { type SchoolReadable } from '../generated/types.gen'
  import { schoolsList, schoolsPartialUpdate } from '../generated/sdk.gen'
  import { setCurrentSchool } from '../stores/data'

  let schools = $state<SchoolReadable[]>([])
  let fetchingGroups = $state<Set<string>>(new Set())
  let fetchingUsers = $state<Set<string>>(new Set())
  let importingGroupsAndUsers = $state<Set<string>>(new Set())
  let alertMessage = $state<string>('')
  let alertType = $state<'success' | 'error' | ''>('')
  let showDetails = $state<boolean>(false)
  let rawJsonResult = $state<any>(null)
  let dryRun = $state(false)
  let overwrite = $state(false)
  let crashOnError = $state(false)
  let feideOrgInput: HTMLInputElement

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

  const feideFetchGroupsForSchool = async (orgNumber: string) => {
    fetchingGroups = new Set([...fetchingGroups, orgNumber])
    dismissAlert()
    try {
      const response = await fetch(`/api/fetch/groups/feide/${orgNumber}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        alertMessage = `✅ Hentet grupper for ${orgNumber} (basis: ${result.basis_groups}, undervisning: ${result.teaching_groups})`
        alertType = 'success'
        rawJsonResult = result
      } else {
        alertMessage = `❌ Feil ved henting av grupper for ${orgNumber}: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    } finally {
      fetchingGroups = new Set([...fetchingGroups].filter(id => id !== orgNumber))
    }
  }

  const feideFetchUsersForSchool = async (orgNumber: string) => {
    fetchingUsers = new Set([...fetchingUsers, orgNumber])
    dismissAlert()
    try {
      const response = await fetch(`/api/fetch/users/feide/${orgNumber}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        alertMessage = `✅ Hentet brukere/medlemskap for ${orgNumber} (grupper: ${result.groups_processed}, brukere: ${result.unique_users})`
        alertType = 'success'
        rawJsonResult = result
      } else {
        alertMessage = `❌ Feil ved henting av brukere for ${orgNumber}: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    } finally {
      fetchingUsers = new Set([...fetchingUsers].filter(id => id !== orgNumber))
    }
  }

  const feideSchoolImport = async (orgNumber: string) => {
    dismissAlert()
    try {
      const response = await fetch(`/api/import/school/feide/${orgNumber}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const result = await response.json()
      if (response.ok && result.status === 'success') {
        alertMessage = `✅ Skole med org.nr ${orgNumber} importert fra Feide!`
        alertType = 'success'
        rawJsonResult = result
        await fetchSchools()
      } else {
        alertMessage = `❌ Feil ved import av skole ${orgNumber}: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    }
  }

  const importGroupsAndUsers = async (orgNumber: string) => {
    dismissAlert()
    importingGroupsAndUsers = new Set([...importingGroupsAndUsers, orgNumber])
    try {
      const response = await fetch(`/api/import/school_groups_and_users/${orgNumber}/`, {
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
        alertMessage = `✅ Grupper og brukere importert for skole ${orgNumber}!`
        alertType = 'success'
        rawJsonResult = result || null
      } else {
        alertMessage = `❌ Feil ved import av grupper og brukere for skole ${orgNumber}: ${result.message || 'Ukjent feil'}`
        alertType = 'error'
      }
    } catch (e: any) {
      alertMessage = `❌ Nettverksfeil: ${e?.message || e}`
      alertType = 'error'
    } finally {
      importingGroupsAndUsers = new Set([...importingGroupsAndUsers].filter(id => id !== orgNumber))
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="py-3">
  <h2>Skoler</h2>

  <div class="mb-4">
    <label for="feideOrgInput" class="form-label">Importer skole fra Feide (org.nr):</label>
    <div class="input-group mb-3" style="max-width: 400px;">
      <input
        type="text"
        class="form-control"
        id="feideOrgInput"
        placeholder="Organisasjonsnummer"
        bind:this={feideOrgInput}
      />
      <button
        class="btn btn-outline-secondary"
        type="button"
        onclick={() => feideSchoolImport(feideOrgInput.value)}
      >
        Importer fra Feide
      </button>
    </div>
    <div class="d-flex align-items-center gap-3 mb-3">
      <div class="form-check form-switch">
        <input class="form-check-input" type="checkbox" bind:checked={dryRun} id="dryRunSwitch" />
        <label class="form-check-label" for="dryRunSwitch">Dry-run (ingen DB-skriving)</label>
      </div>
      <div class="form-check form-switch">
        <input
          class="form-check-input"
          type="checkbox"
          bind:checked={overwrite}
          id="overwriteSwitch"
        />
        <label class="form-check-label" for="overwriteSwitch">Overwrite eksisterende</label>
      </div>
      <div class="form-check form-switch">
        <input
          class="form-check-input"
          type="checkbox"
          bind:checked={crashOnError}
          id="crashSwitch"
        />
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
                <div class="mt-2 pt-2 border-top">
                  <small class="text-muted">Response:</small>
                  <pre class="json-display">{JSON.stringify(rawJsonResult, null, 2)}</pre>
                </div>
              {/if}
            {/if}
          </div>

          <button type="button" class="btn-close" onclick={dismissAlert} aria-label="Lukk"></button>
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
                      {school.orgNumber} • Sist oppdatert: {new Date(
                        school.updatedAt
                      ).toLocaleString('nb-NO')}
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
                  class="btn btn-outline-secondary btn-sm"
                  onclick={() => feideFetchGroupsForSchool(school.orgNumber)}
                  disabled={fetchingGroups.has(school.orgNumber)}
                >
                  {#if fetchingGroups.has(school.orgNumber)}
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Henter grupper...
                  {:else}
                    🔁 Hent grupper
                  {/if}
                </button>
                <button
                  class="btn btn-outline-secondary btn-sm"
                  onclick={() => feideFetchUsersForSchool(school.orgNumber)}
                  disabled={fetchingUsers.has(school.orgNumber)}
                >
                  {#if fetchingUsers.has(school.orgNumber)}
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Henter brukere...
                  {:else}
                    👥 Hent brukere
                  {/if}
                </button>
                <button
                  class="btn btn-outline-primary btn-sm"
                  onclick={() => importGroupsAndUsers(school.orgNumber)}
                  disabled={importingGroupsAndUsers.has(school.orgNumber)}
                >
                  {#if importingGroupsAndUsers.has(school.orgNumber)}
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Importerer...
                  {:else}
                    📥 Importer
                  {/if}
                </button>

                <div class="form-check form-switch">
                  <input
                    id={"service-" + school.id}
                    class="form-check-input"
                    type="checkbox"
                    checked={school.isServiceEnabled}
                    onchange={() => toggleServiceEnabled(school)}
                  />
                  <label class="form-check-label" for={"service-" + school.id}>
                    {school.isServiceEnabled ? 'Aktiv' : 'Inaktiv'}
                  </label>
                </div>
              </div>
            </div>
          </div>
        {/each}
      {/if}
    </div>
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

  .json-display {
    margin: 0;
    padding: 1rem;
    background-color: #f8f9fa;
    max-height: 400px;
    overflow-y: auto;
  }
</style>
