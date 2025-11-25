<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type SchoolType } from '../../generated/types.gen'
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
  import { addAlert } from '../../stores/alerts'

  const router = useTinyRouter()
  let schools = $state<SchoolType[]>([])
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
      addAlert({
        type: 'danger',
        message: `Feil ved henting av importstatus for skole ${orgNumber}`,
      })
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
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av skoler',
      })
      schools = []
    }
  }

  const toggleServiceEnabled = async (school: SchoolType) => {
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
      addAlert({
        type: 'danger',
        message: `Feil ved oppdatering av status for skole ${school.displayName}`,
      })
    }
  }

  // Toggle whether group goals can be created at the school
  const toggleGroupGoalEnabled = async (school: SchoolType) => {
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

  // Toggle whether group title is displayed in goal edit
  const toggleGoalTitleEnabled = async (school: SchoolType) => {
    try {
      const current = (school as any).isGoalTitleEnabled ?? false
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isGoalTitleEnabled: !current },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating isGoalTitleEnabled:', error)
    }
  }

  // Toggle whether teachers can see the students list menu item
  const toggleStudentListEnabled = async (school: SchoolType) => {
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

  const updateSubjectsAllowed = async (school: SchoolType, value: SubjectsAllowed) => {
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

  const handleFetchGroupsForSchool = async (orgNumber: string) => {
    try {
      const result = await fetchGroupsForSchool({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for henting av grupper for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks')
      } else if (result.response.status === 409) {
        addAlert({
          type: 'warning',
          message: `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`,
        })
      } else {
        addAlert({
          type: 'danger',
          message: `Feil ved oppretting av bakgrunnsjobb for ${orgNumber}`,
        })
      }
    } catch (error: any) {
      addAlert({
        type: 'danger',
        message: `Nettverksfeil: ${error?.message || error}`,
      })
    }
  }

  const handleFetchMembershipsForSchool = async (orgNumber: string) => {
    try {
      const result = await fetchMembershipsForSchool({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for henting av medlemskap for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks')
      } else if (result.response.status === 409) {
        addAlert({
          type: 'warning',
          message: `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`,
        })
      } else {
        addAlert({
          type: 'danger',
          message: `Feil ved oppretting av bakgrunnsjobb for ${orgNumber}`,
        })
      }
    } catch (error: any) {
      addAlert({
        type: 'danger',
        message: `Nettverksfeil: ${error?.message || error}`,
      })
    }
  }

  const handleImportSchool = async (orgNumber: string) => {
    try {
      const result = await feideImportSchool({
        path: { org_number: orgNumber },
      } as any)
      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Skole med org nr ${orgNumber} importert fra Feide`,
        })
        await fetchSchools()
        feideOrgInput.value = ''
      } else {
        addAlert({
          type: 'danger',
          message: `Feil ved import av skole ${orgNumber}`,
        })
      }
    } catch (error: any) {
      addAlert({
        type: 'danger',
        message: `Nettverksfeil: ${error?.message || error}`,
      })
    }
  }

  const handleImportGroupsAndUsers = async (orgNumber: string) => {
    try {
      const result = await importGroupsAndUsers({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for import av grupper og brukere for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks')
      } else if (result.response.status === 409) {
        addAlert({
          type: 'warning',
          message: `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det allerede finnes en pågående jobb.`,
        })
      } else {
        addAlert({
          type: 'danger',
          message: `Feil ved oppretting av importbakgrunnsjobb for ${orgNumber}`,
        })
      }
    } catch (error: any) {
      addAlert({
        type: 'danger',
        message: `Nettverksfeil: ${error?.message || error}`,
      })
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

  {#each schools as school}
    <div class="border border-3 mb-4" class:opacity-25={!school.isServiceEnabled}>
      <div class="p-4">
        <div class="d-flex align-items-center">
          <h3>{school.displayName}</h3>
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

        <!-- Subjects -->
        <h4 class="my-4">Fag</h4>
        <p class="mb-3">Hvilke fag er tilgjengelige på skolen?</p>
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
        <hr />

        <!-- Groups -->
        <h4 class="my-4">Grupper</h4>
        <pkt-checkbox
          id={'group-goal-' + school.id}
          label={`Gruppemål ${(school as any).isGroupGoalEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={(school as any).isGroupGoalEnabled}
          checked={(school as any).isGroupGoalEnabled}
          onchange={() => toggleGroupGoalEnabled(school)}
        ></pkt-checkbox>

        <pkt-checkbox
          id={'goal-title' + school.id}
          class="ms-1"
          label={`Fritekst-tittel på mål ${(school as any).isGoalTitleEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={(school as any).isGoalTitleEnabled}
          checked={(school as any).isGoalTitleEnabled}
          onchange={() => toggleGoalTitleEnabled(school)}
        ></pkt-checkbox>
        <hr />

        <!-- Groups -->
        <h4 class="my-4">Navigasjon for lærere</h4>
        <pkt-checkbox
          id={'student-list-' + school.id}
          label={`Elevliste ${(school as any).isStudentListEnabled ? '' : 'IKKE'} synlig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={(school as any).isStudentListEnabled}
          checked={(school as any).isStudentListEnabled}
          onchange={() => toggleStudentListEnabled(school)}
        ></pkt-checkbox>
        <hr />

        <!-- Import status -->
        <h4 class="mt-4 mb-3">Importstatus</h4>
        {#if importStatus[school.orgNumber]}
          <div class="table-responsive">
            <table class="table table-sm align-middle">
              <thead>
                <tr class="border-bottom">
                  <th class="border-0 fw-semibold text-dark small pb-2">Type</th>
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">Hentet</th>
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">Database</th>
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">Forskjell</th>
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">Sist hentet</th>
                </tr>
              </thead>

              <tbody>
                <!-- Users -->
                <tr class="border-0">
                  <td class="border-0 py-2">
                    <div class="d-flex align-items-center">
                      <pkt-icon name="person" size="16" class="me-2 text-muted"></pkt-icon>
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

                <!-- Groups -->
                <tr class="border-0">
                  <td class="border-0 py-2">
                    <div class="d-flex align-items-center">
                      <pkt-icon name="group" size="16" class="me-2 text-muted"></pkt-icon>
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

                <!-- Memberships -->
                <tr class="border-0">
                  <td class="border-0 py-2">
                    <div class="d-flex align-items-center">
                      <pkt-icon name="holding-hands" size="16" class="me-2 text-muted"></pkt-icon>
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
        {/if}

        <div>
          <!-- Hent grupper -->
          <ButtonMini
            options={{
              title: 'Hent grupper fra Feide',
              iconName: 'group',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchGroupsForSchool(school.orgNumber),
            }}
          >
            Hent grupper fra Feide
          </ButtonMini>

          <!-- Hent brukere -->
          <ButtonMini
            options={{
              title: 'Hent brukere fra Feide',
              iconName: 'person',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchMembershipsForSchool(school.orgNumber),
            }}
          >
            Hent brukere fra Feide
          </ButtonMini>

          <!-- Importer -->
          <ButtonMini
            options={{
              title: 'Importér',
              iconName: 'download',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleImportGroupsAndUsers(school.orgNumber),
            }}
          >
            Importér
          </ButtonMini>
        </div>
      </div>
    </div>
  {/each}
</section>

<style>
</style>
