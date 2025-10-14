<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type SchoolReadable } from '../../generated/types.gen'
  import {
    fetchGroupsForSchool,
    fetchMembershipsForSchool,
    fetchSchoolImportStatus,
    importGroupsAndUsers,
    feideImportSchool,
    schoolsList,
    schoolsPartialUpdate,
  } from '../../generated/sdk.gen'
  import type { SchoolImportStatus } from '../../types/models'
  import { formatDate } from '../../utils/functions'

  import ButtonMini from '../../components/ButtonMini.svelte'

  const router = useTinyRouter()
  let schools = $state<SchoolReadable[]>([])
  let alertMessage = $state<string>('')
  let alertType = $state<'success' | 'error' | ''>('')
  let feideOrgInput: HTMLInputElement

  // Radio options for subject config
  const subjectOptions = [
    { value: 'all', label: 'Alle fag' },
    { value: 'only-group', label: 'Kun fag via Feide-grupper' },
    { value: 'only-custom', label: 'Kun egendefinerte fag' },
  ] as const

  let importStatus = $state<Record<string, SchoolImportStatus>>({})

  const loadImportStatusForSchool = async (orgNumber: string) => {
    try {
      const result = await fetchSchoolImportStatus({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 200 && result.data) {
        const data = result.data as SchoolImportStatus
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

  // Toggle whether group goals can be created at the school
  const toggleGroupGoalEnabled = async (school: SchoolReadable) => {
    try {
      const current = (school as any).isGroupGoalEnabled ?? false
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isGroupGoalEnabled: !current },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating isGroupGoalEnabled:', error)
    }
  }

  // Toggle whether teachers can see the students list menu item
  const toggleStudentListEnabled = async (school: SchoolReadable) => {
    try {
      const current = (school as any).isStudentListEnabled ?? false
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isStudentListEnabled: !current },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating isStudentListEnabled:', error)
    }
  }

  type SubjectsAllowed = 'only-custom' | 'only-group' | 'all'

  const updateSubjectsAllowed = async (school: SchoolReadable, value: SubjectsAllowed) => {
    if (school.subjectsAllowed === value) return
    try {
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { subjectsAllowed: value },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating subjectsAllowed:', error)
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
      } as any)

      if (result.response.status === 201) {
        // @ts-expect-error result.data typed as unknown by generator
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
      } as any)

      if (result.response.status === 201) {
        // @ts-expect-error result.data typed as unknown by generator
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
      } as any)
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
      } as any)

      if (result.response.status === 201) {
        // @ts-expect-error result.data typed as unknown by generator
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
  <h2>Dataimport og konfig for skoler</h2>

  <!-- Import school by org number -->
  <div class="py-4">
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
              class="ms-auto"
              label={school.isServiceEnabled ? 'Aktivert' : 'Deaktivert'}
              labelPosition="right"
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

        <div class="mb-2">Hvilke fag er tilgjengelige på skolen</div>

        <!-- Radio buttons for filtering groups -->
        <fieldset class="d-flex flex-wrap gap-4">
          {#each subjectOptions as option}
            <pkt-radiobutton
              name={'subjectsAllowed-' + school.id}
              value={option.value}
              label={option.label}
              checked={school.subjectsAllowed === option.value}
              onchange={() => updateSubjectsAllowed(school, option.value)}
            ></pkt-radiobutton>
          {/each}
        </fieldset>
        <div>
          <pkt-checkbox
            id={'group-goal-' + school.id}
            class="mb-0 ms-3"
            label={(school as any).isGroupGoalEnabled
              ? 'Gruppemål tilgjengelig'
              : 'Gruppemål ikke tilgjgengelig'}
            labelPosition="right"
            isSwitch="true"
            aria-checked={(school as any).isGroupGoalEnabled}
            checked={(school as any).isGroupGoalEnabled}
            onchange={() => toggleGroupGoalEnabled(school)}
          ></pkt-checkbox>
        </div>
        <div>
          <pkt-checkbox
            id={'student-list-' + school.id}
            class="mb-0 ms-3"
            label={(school as any).isStudentListEnabled
              ? 'Elevliste synlig'
              : 'Elevliste ikke synlig'}
            labelPosition="right"
            isSwitch="true"
            aria-checked={(school as any).isStudentListEnabled}
            checked={(school as any).isStudentListEnabled}
            onchange={() => toggleStudentListEnabled(school)}
          ></pkt-checkbox>
        </div>

        {#if importStatus[school.orgNumber]}
          <div class="my-4">
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
</style>
