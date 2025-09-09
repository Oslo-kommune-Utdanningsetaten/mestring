<script lang="ts">
  import { type SchoolReadable } from '../generated/types.gen'
  import {
    fetchGroupsForSchool,
    fetchMembershipsForSchool,
    fetchSchoolImportStatus,
    importGroupsAndUsers,
    feideImportSchool,
    schoolsList,
    schoolsPartialUpdate,
  } from '../generated/sdk.gen'
  import { setCurrentSchool } from '../stores/data'

  let schools = $state<SchoolReadable[]>([])
  let alertMessage = $state<string>('')
  let alertType = $state<'success' | 'error' | ''>('')
  let showDetails = $state<boolean>(false)
  let rawJsonResult = $state<any>(null)
  let overwrite = $state(false)
  let crashOnError = $state(false)
  let feideOrgInput: HTMLInputElement
  let readiness = $state<Record<string, { groups: number; users: number }>>({})

  type ImportStatus = {
    groups: {
      fetchedCount: number | null
      fetchedAt: string | null
      dbCount: number | null
      diff: number | null
    }
    users: {
      fetchedCount: number | null
      fetchedAt: string | null
      dbCount: number | null
      diff: number | null
    }
    memberships: {
      fetchedCount: number | null
      fetchedAt: string | null
      dbCount: number | null
      diff: number | null
    }
    lastImportAt: string | null
  }
  let importStatus = $state<Record<string, ImportStatus>>({})

  const formatDate = (iso?: string | null) => (iso ? new Date(iso).toLocaleString('nb-NO') : '—')

  const loadImportStatusForSchool = async (orgNumber: string) => {
    try {
      const response = await fetchSchoolImportStatus({
        path: { org_number: orgNumber },
      })

      const data = response.data as any 

      if (data?.status === 'success') {
        importStatus = {
          ...importStatus,
          [orgNumber]: {
            groups: {
              fetchedCount: data.groups?.fetchedCount ?? null,
              fetchedAt: data.groups?.fetchedAt ?? null,
              dbCount: data.groups?.dbCount ?? 0,
              diff: data.groups?.diff ?? null,
            },
            users: {
              fetchedCount: data.users?.fetchedCount ?? null,
              fetchedAt: data.users?.fetchedAt ?? null,
              dbCount: data.users?.dbCount ?? 0,
              diff: data.users?.diff ?? null,
            },
            memberships: {
              fetchedCount: data.memberships?.fetchedCount ?? null,
              fetchedAt: data.memberships?.fetchedAt ?? null,
              dbCount: data.memberships?.dbCount ?? 0,
              diff: data.memberships?.diff ?? null,
            },
            lastImportAt: data.lastImportAt ?? null,
          },
        }
      }
    } catch (error) {
      console.error('Error fetching import status:', orgNumber, error)
    }
  }

  const fetchSchools = async () => {
  try {
    const result = await schoolsList()
    schools = result.data || []
    await Promise.all(
      schools.map(school => loadImportStatusForSchool(school.orgNumber))
    )
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

  const handleFetchGroupsForSchool = async (orgNumber: string) => {
  dismissAlert()
  
  try {
    const result = await fetchGroupsForSchool({
      path: { org_number: orgNumber },
    })
    
    if (result.response.status === 201) {
      alertMessage = `✅ Bakgrunnns jobb opprettet for henting av grupper for ${orgNumber} (Task ID: ${result.data.taskId})`
      alertType = 'success'
    } else {
      alertMessage = `❌ Feil ved oppretting av bakgrunnns jobb for ${orgNumber}`
      alertType = 'error'
    }
  } catch (error: any) {
    alertMessage = `❌ Nettverksfeil: ${error?.message || error}`
    alertType = 'error'
  }
}


  const handleFetchMembershipsForSchool = async (orgNumber: string) => {
    dismissAlert()
    try {
      const result = await fetchMembershipsForSchool({
        path: { org_number: orgNumber },
      })

      if (result.response.status === 201) {
        alertMessage = `✅ Bakgrunnns jobb opprettet for henting av medlemskap for ${orgNumber} (Task ID: ${(result.data as any).taskId})`
        alertType = 'success'
      } else {
        alertMessage = `❌ Feil ved oppretting av bakgrunnns jobb for ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `❌ Nettverksfeil: ${error?.message || error}`
      alertType = 'error'
    }
  }

  
  const handleImportSchool = async (orgNumber: string) => {
    dismissAlert()

    try {
      const result = await feideImportSchool({
        path: { org_number: orgNumber },
      })
      if (result.response.status === 201) {
        alertMessage = `✅ Skole med org nr ${orgNumber} importert fra Feide!`
        alertType = 'success'
        // Refresh schools list
        await fetchSchools()
      } else {
        alertMessage = `❌ Feil ved import av skole ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `❌ Nettverksfeil: ${error?.message || error}`
      alertType = 'error'
    }
  }
  
  const handleImportGroupsAndUsers = async (orgNumber: string) => {
    dismissAlert()

    try {
      const result = await importGroupsAndUsers({
        path: { org_number: orgNumber },
        body: {
          is_overwrite_enabled: overwrite,
          is_crash_on_error_enabled: crashOnError,
        },
      })

      if (result.response.status === 201) {
        alertMessage = `✅ Bakgrunnns jobb opprettet for import av grupper og brukere for ${orgNumber} (Task ID: ${result.data.taskId})`
        alertType = 'success'
      } else {
        alertMessage = `❌ Feil ved oppretting av importbakgrunnns jobb for ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `❌ Nettverksfeil: ${error?.message || error}`
      alertType = 'error'
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
    <div class="col-12 col-sm-8 col-md-6 col-lg-4">
      <div class="input-group mb-3">
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
          onclick={() => handleImportSchool(feideOrgInput.value)}
        >
          Importer fra Feide
        </button>
      </div>
    </div>
    <div class="d-flex align-items-center gap-3 mb-3">
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
                  <small class="text-muted">Raw JSON:</small>
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
                    {school.orgNumber} • Sist oppdatert: {formatDate(school.updatedAt)}
                  </small>
                {/if}

                {#if importStatus[school.orgNumber]}
                  <div class="mt-3 small">
                    <table class="table table-bordered align-middle w-100">
                      <thead class="table-light">
                        <tr>
                          <th scope="col">Type</th>
                          <th scope="col">Hentet</th>
                          <th scope="col">DB</th>
                          <th scope="col">Forskjell</th>
                          <th scope="col">Sist hentet</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td><strong>Grupper</strong></td>
                          <td>{importStatus[school.orgNumber].groups.fetchedCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].groups.dbCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].groups.diff ?? '—'}</td>
                          <td>{formatDate(importStatus[school.orgNumber].groups.fetchedAt)}</td>
                        </tr>
                        <tr>
                          <td><strong>Brukere</strong></td>
                          <td>{importStatus[school.orgNumber].users.fetchedCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].users.dbCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].users.diff ?? '—'}</td>
                          <td>{formatDate(importStatus[school.orgNumber].users.fetchedAt)}</td>
                        </tr>
                        <tr>
                          <td><strong>Medlemskap</strong></td>
                          <td>{importStatus[school.orgNumber].memberships.fetchedCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].memberships.dbCount ?? '—'}</td>
                          <td>{importStatus[school.orgNumber].memberships.diff ?? '—'}</td>
                          <td>{formatDate(importStatus[school.orgNumber].users.fetchedAt)}</td>
                        </tr>
                      </tbody>
                    </table>

                    <div class="text-muted">
                      ⏱️ Sist import: {formatDate(importStatus[school.orgNumber].lastImportAt)}
                    </div>
                  </div>
                {/if}
              </div>

              <div class="d-flex align-items-center gap-2">
                <!-- Groups -->
                <button
                  class="btn btn-outline-secondary btn-sm"
                  onclick={() => handleFetchGroupsForSchool(school.orgNumber)}
                >
                  🔁 Hent grupper
                </button>

                <!-- Memberships -->
                <button
                  class="btn btn-outline-secondary btn-sm"
                  onclick={() => handleFetchMembershipsForSchool(school.orgNumber)}
                >
                  👥 Hent brukere
                </button>

                <!-- Import -->
                <button
                  class="btn btn-outline-primary btn-sm"
                  onclick={() => handleImportGroupsAndUsers(school.orgNumber)}
                >
                  📥 Importer
                  {#if readiness[school.orgNumber]}
                    <span class="ms-2 text-muted small">
                      ({readiness[school.orgNumber].groups} grupper, {readiness[school.orgNumber]
                        .users} brukere)
                    </span>
                  {/if}
                </button>

                <div class="form-check form-switch">
                  <input
                    id={'service-' + school.id}
                    class="form-check-input"
                    type="checkbox"
                    checked={school.isServiceEnabled}
                    onchange={() => toggleServiceEnabled(school)}
                  />
                  <label class="form-check-label" for={'service-' + school.id}>
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

  .json-display {
    margin: 0;
    padding: 1rem;
    background-color: #f8f9fa;
    max-height: 400px;
    overflow-y: auto;
  }
</style>
