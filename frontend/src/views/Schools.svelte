<script lang="ts">
  import ButtonMini from '../components/ButtonMini.svelte'
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
  import { useTinyRouter } from 'svelte-tiny-router'

  const router = useTinyRouter()
  let schools = $state<SchoolReadable[]>([])
  let alertMessage = $state<string>('')
  let alertType = $state<'success' | 'error' | ''>('')
  let feideOrgInput: HTMLInputElement

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

  const schoolOptions = $derived(
    schools.map(school => ({
      label: school.displayName,
      value: school.id,
    }))
  )

  const loadImportStatusForSchool = async (orgNumber: string) => {
    try {
      const result = await fetchSchoolImportStatus({
        path: { org_number: orgNumber },
      })

      if (result.response.status === 200 && result.data) {
        const data = result.data as ImportStatus
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
              fetchedAt: data.users?.fetchedAt ?? null,
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
      schools = (result.data || [])
        .sort((a, b) => a.displayName.localeCompare(b.displayName, 'nb', { sensitivity: 'base' }))
        .sort((a, b) => Number(!a.isServiceEnabled) - Number(!b.isServiceEnabled))
      await Promise.all(schools.map(school => loadImportStatusForSchool(school.orgNumber)))
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
  }

  const handleFetchGroupsForSchool = async (orgNumber: string) => {
    dismissAlert()
    try {
      const result = await fetchGroupsForSchool({
        path: { org_number: orgNumber },
      })

      if (result.response.status === 201) {
        alertMessage = `Bakgrunnsjobb opprettet for henting av grupper for ${orgNumber} (Task ID: ${result.data.taskId})`
        alertType = 'success'
      } else if (result.response.status === 409) {
        alertMessage = `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`
        alertType = 'error'
      } else {
        alertMessage = `Feil ved oppretting av bakgrunnsjobb for ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `Nettverksfeil: ${error?.message || error}`
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
        alertMessage = `Bakgrunnsjobb opprettet for henting av medlemskap for ${orgNumber} (Task ID: ${result.data.taskId})`
        alertType = 'success'
      } else if (result.response.status === 409) {
        alertMessage = `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`
        alertType = 'error'
      } else {
        alertMessage = `Feil ved oppretting av bakgrunnsjobb for ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `Nettverksfeil: ${error?.message || error}`
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
        alertMessage = `Skole med org nr ${orgNumber} importert fra Feide`
        alertType = 'success'
        await fetchSchools()
        feideOrgInput.value = ''
      } else {
        alertMessage = `Feil ved import av skole ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `Nettverksfeil: ${error?.message || error}`
      alertType = 'error'
    }
  }

  const handleImportGroupsAndUsers = async (orgNumber: string) => {
    dismissAlert()
    try {
      const result = await importGroupsAndUsers({
        path: { org_number: orgNumber },
      })

      if (result.response.status === 201) {
        alertMessage = `Bakgrunnsjobb opprettet for import av grupper og brukere for ${orgNumber} (Task ID: ${result.data.taskId})`
        alertType = 'success'
        router.navigate('/data-maintenance-tasks')
      } else if (result.response.status === 409) {
        alertMessage = `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`
        alertType = 'error'
      } else {
        alertMessage = `Feil ved oppretting av importbakgrunnsjobb for ${orgNumber}`
        alertType = 'error'
      }
    } catch (error: any) {
      alertMessage = `Nettverksfeil: ${error?.message || error}`
      alertType = 'error'
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="container py-3">
  <h1>Dataimport for skoler</h1>

  <!-- Import school by org number -->
  <div class="shadow-sm p-4 mb-4">
    <pkt-textinput
      label="Legg til ny skole"
      placeholder="Organisasjonsnummer"
      autocomplete="off"
      class="mb-2"
      bind:this={feideOrgInput}
    ></pkt-textinput>
    <ButtonMini
      options={{
        title: 'Legg til ny skole',
        iconName: 'plus-sign',
        skin: 'primary',
        variant: 'icon-left',
        onClick: () => handleImportSchool(feideOrgInput.value),
      }}
    >
      Legg til ny skole
    </ButtonMini>
  </div>

  <!-- Alert -->
  {#if alertMessage}
    <div
      class="alert alert-{alertType === 'success' ? 'success' : 'danger'} border-0 mb-0 mt-3"
      role="alert"
    >
      <div class="d-flex align-items-start">
        <pkt-icon
          name={alertType === 'success' ? 'checkmark-circle' : 'error-circle'}
          size="20"
          class="me-2 mt-0 flex-shrink-0"
        ></pkt-icon>
        <div class="flex-grow-1">
          <div class="small fw-medium">{alertMessage}</div>
        </div>
        <button
          type="button"
          class="btn-close btn-close-sm"
          onclick={dismissAlert}
          aria-label="Lukk"
        ></button>
      </div>
    </div>
  {/if}

  {#each schools as school}
    <div class="border border-1 mb-4" class:opacity-25={!school.isServiceEnabled}>
      <div class="p-4">
        <div class="row align-items-start mb-4">
          <div class="d-flex align-items-center">
            <h5>{school.displayName}</h5>
            <pkt-checkbox
              id={'service-' + school.id}
              class="mb-0 ms-auto"
              label={school.isServiceEnabled ? 'Aktiv' : 'Inaktiv'}
              labelPosition="left"
              isSwitch="true"
              aria-checked={school.isServiceEnabled}
              checked={school.isServiceEnabled}
              onchange={() => toggleServiceEnabled(school)}
            ></pkt-checkbox>
          </div>

          <div class="text-muted small">
            {school.orgNumber}, Oppdatert {formatDate(school.updatedAt)}
          </div>
        </div>

        {#if importStatus[school.orgNumber]}
          <div class="mb-4">
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr class="border-bottom">
                    <th class="border-0 fw-semibold text-dark small pb-2">Type</th>
                    <th class="border-0 fw-semibold text-dark small text-center pb-2">Hentet</th>
                    <th class="border-0 fw-semibold text-dark small text-center pb-2">Database</th>
                    <th class="border-0 fw-semibold text-dark small text-center pb-2">Forskjell</th>
                    <th class="border-0 fw-semibold text-dark small text-center pb-2">
                      Sist hentet
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-0">
                    <td class="border-0 py-2">
                      <div class="d-flex align-items-center">
                        <pkt-icon name="folder" size="16" class="me-2 text-muted"></pkt-icon>
                        <span class="small">Grupper</span>
                      </div>
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].groups.fetchedCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].groups.dbCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].groups.diff ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small text-muted">
                      {formatDate(importStatus[school.orgNumber].groups.fetchedAt)}
                    </td>
                  </tr>
                  <tr class="border-0">
                    <td class="border-0 py-2">
                      <div class="d-flex align-items-center">
                        <pkt-icon
                          name="two-people-dancing"
                          size="16"
                          class="me-2 text-muted"
                        ></pkt-icon>
                        <span class="small">Brukere</span>
                      </div>
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].users.fetchedCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].users.dbCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].users.diff ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small text-muted">
                      {formatDate(importStatus[school.orgNumber].users.fetchedAt)}
                    </td>
                  </tr>
                  <tr class="border-0">
                    <td class="border-0 py-2">
                      <div class="d-flex align-items-center">
                        <pkt-icon name="link" size="16" class="me-2 text-muted"></pkt-icon>
                        <span class="small">Medlemskap</span>
                      </div>
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].memberships.fetchedCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].memberships.dbCount ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small">
                      {importStatus[school.orgNumber].memberships.diff ?? '—'}
                    </td>
                    <td class="border-0 text-center py-2 small text-muted">
                      {formatDate(importStatus[school.orgNumber].memberships.fetchedAt)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {#if importStatus[school.orgNumber].lastImportAt}
              <div class="d-flex align-items-center mt-3 pt-3 border-top">
                <pkt-icon name="clock" size="16" class="me-2 text-muted"></pkt-icon>
                <span class="text-muted small">
                  Sist import: {formatDate(importStatus[school.orgNumber].lastImportAt)}
                </span>
              </div>
            {/if}
          </div>
        {/if}

        <div>
          <!-- Hent grupper -->
          <ButtonMini
            options={{
              title: 'Hent grupper',
              iconName: 'folder',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchGroupsForSchool(school.orgNumber),
            }}
          >
            Hent grupper
          </ButtonMini>

          <!-- Hent brukere -->
          <ButtonMini
            options={{
              title: 'Hent brukere',
              iconName: 'two-people-dancing',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchMembershipsForSchool(school.orgNumber),
            }}
          >
            Hent brukere
          </ButtonMini>

          <!-- Importer -->
          <ButtonMini
            options={{
              title: 'Importer',
              iconName: 'download',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleImportGroupsAndUsers(school.orgNumber),
            }}
          >
            Importer
          </ButtonMini>
        </div>
      </div>
    </div>
  {/each}
</section>

<style>
  .card {
    transition: box-shadow 0.15s ease-in-out;
  }

  .card:hover {
    box-shadow: 0 0.25rem 1rem rgba(0, 0, 0, 0.08) !important;
  }
</style>
