<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type SchoolType } from '../../generated/types.gen'
  import {
    fetchGroupsAndUsers,
    fetchSchoolImportStatus,
    importGroupsAndUsers,
    feideImportSchool,
    schoolsList,
    schoolsPartialUpdate,
    updateDataIntegrity,
    estimateGroupsImport,
    estimateUsersImport,
    estimateMembershipsImport,
  } from '../../generated/sdk.gen'
  import type { SchoolImportStatus } from '../../types/models'
  import { formatDateTime } from '../../utils/functions'
  import {
    SUBJECTS_ALLOWED_ALL,
    SUBJECTS_ALLOWED_CUSTOM,
    SUBJECTS_ALLOWED_FEIDE,
  } from '../../utils/constants'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import { addAlert } from '../../stores/alerts'
  import { dataStore } from '../../stores/data'
  import { es } from 'date-fns/locale'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import ImportEstimate from '../../components/ImportEstimate.svelte'

  const router = useTinyRouter()
  let schools = $state<SchoolType[]>([])
  let feideOrgInput: HTMLInputElement
  let currentEstimate = $state<Record<string, any> | null>(null)
  let isEstimateContainerOpen = $state<boolean>(false)

  // Radio options for subject config
  const subjectOptions = [
    { value: SUBJECTS_ALLOWED_ALL, label: 'Alle fag' },
    { value: SUBJECTS_ALLOWED_FEIDE, label: 'Kun fag via Feide-grupper' },
    { value: SUBJECTS_ALLOWED_CUSTOM, label: 'Kun egendefinerte fag' },
  ] as const

  let importStatus = $state<Record<string, SchoolImportStatus>>({})

  const loadImportStatusForSchool = async (orgNumber: string) => {
    try {
      const result = await fetchSchoolImportStatus({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 200 && result.data) {
        const data = result.data as SchoolImportStatus
        const { groups, users, memberships, lastImportAt } = data
        importStatus = {
          ...importStatus,
          [orgNumber]: {
            groups: {
              fetchedCount: groups?.fetchedCount,
              fetchedAt: groups?.fetchedAt,
              dbCount: groups?.dbCount || 0,
              diff: groups?.diff,
            },
            users: {
              fetchedCount: users?.fetchedCount,
              fetchedAt: users?.fetchedAt,
              dbCount: users?.dbCount || 0,
              diff: users?.diff,
            },
            memberships: {
              fetchedCount: memberships?.fetchedCount,
              fetchedAt: users?.fetchedAt,
              dbCount: memberships?.dbCount || 0,
              diff: memberships?.diff,
            },
            lastImportAt: lastImportAt,
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
      const currentSchoolId = $dataStore.currentSchool?.id

      let fetchedSchools = (result.data || [])
        .sort((a, b) => a.displayName.localeCompare(b.displayName, 'nb', { sensitivity: 'base' }))
        .sort((a, b) => Number(!a.isServiceEnabled) - Number(!b.isServiceEnabled))

      if (currentSchoolId) {
        const currentSchoolIndex = fetchedSchools.findIndex(s => s.id === currentSchoolId)
        if (currentSchoolIndex > -1) {
          const [currentSchool] = fetchedSchools.splice(currentSchoolIndex, 1)
          fetchedSchools.unshift(currentSchool)
        }
      }
      schools = fetchedSchools
      await Promise.all(schools.map(school => loadImportStatusForSchool(school.orgNumber)))
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av skoler',
      })
      schools = []
    }
  }

  const handleUpdateEstimate = async (orgNumber: string, dataType: string) => {
    isEstimateContainerOpen = true
    let result = null
    if (dataType === 'groups') {
      result = await estimateGroupsImport({ path: { org_number: orgNumber } })
    } else if (dataType === 'users') {
      result = await estimateUsersImport({ path: { org_number: orgNumber } })
    } else if (dataType === 'memberships') {
      result = await estimateMembershipsImport({ path: { org_number: orgNumber } })
    }
    currentEstimate = result?.data || null
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

  // Toggle whether statuses can be created at the school
  const toggleStatusEnabled = async (school: SchoolType) => {
    try {
      const current = (school as any).isStatusEnabled ?? false
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isStatusEnabled: !current },
      })
      const index = schools.findIndex(s => s.id === school.id)
      if (index >= 0 && result.data) {
        schools[index] = result.data
      }
    } catch (error) {
      console.error('Error updating isStatusEnabled:', error)
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

  type SubjectsAllowed = 'only-custom' | 'only-feide' | 'all'

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

  const handleActivateCleanerBotForSchool = async (orgNumber: string) => {
    const confirmed = confirm(`Er du helt sikker på at du vil kjøre ryddejobb for ${orgNumber}?`)

    if (!confirmed) return

    try {
      const result = await updateDataIntegrity({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for sletting av snargh for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks')
      } else if (result.response.status === 400) {
        addAlert({
          type: 'warning',
          message: `Kan ikke opprette ny bakgrunnsjobb for ${orgNumber} fordi det aldri har blitt kjørt en import.`,
        })
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

  const handleFetchUsersAndGroups = async (orgNumber: string) => {
    try {
      const result = await fetchGroupsAndUsers({
        path: { org_number: orgNumber },
      } as any)

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Opprettet bakgrunnsjobber for henting av grupper og brukere for ${orgNumber}`,
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
          message: `Feil ved oppretting av bakgrunnsjobber for ${orgNumber}`,
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
          {school.orgNumber}, Oppdatert {formatDateTime(school.updatedAt)}
        </div>

        <!-- Subjects -->
        <h4 class="my-4">Fag</h4>
        <p class="mb-3">Hvilke fag er tilgjengelige på skolen?</p>
        <fieldset class="d-flex flex-wrap gap-4">
          <legend class="visually-hidden">Velg hvilke fag som er tilgjengelige på skolen</legend>
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

        <!-- Status -->
        <h4 class="my-4">Status</h4>
        <pkt-checkbox
          id={'status-' + school.id}
          label={`Status ${(school as any).isStatusEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={(school as any).isStatusEnabled}
          checked={(school as any).isStatusEnabled}
          onchange={() => toggleStatusEnabled(school)}
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
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">
                    Diff on import
                  </th>
                  <th class="border-0 fw-semibold text-dark small text-center pb-2">
                    Diff on clean
                  </th>
                </tr>
              </thead>

              <tbody>
                <!-- Groups -->
                <tr class="border-0">
                  <td class="border-0 py-2">
                    <div class="d-flex align-items-center">
                      <pkt-icon name="group" size="16" class="me-2 text-muted"></pkt-icon>
                      <span class="small">Grupper</span>
                    </div>
                  </td>
                  <td class="border-0 text-center py-2 small">
                    <span
                      title={`Sist hentet: ${formatDateTime(importStatus[school.orgNumber].groups.fetchedAt)}`}
                    >
                      {importStatus[school.orgNumber].groups.fetchedCount ?? '—'}
                    </span>
                  </td>
                  <td class="border-0 text-center py-2 small">
                    {importStatus[school.orgNumber].groups.dbCount ?? '—'}
                  </td>
                  <td class="border-0 text-center py-2 small">
                    <ButtonMini
                      options={{
                        title: 'Sjekk import',
                        iconName: 'arrow-circle',
                        skin: 'primary',
                        variant: 'icon-left',
                        onClick: () => handleUpdateEstimate(school.orgNumber, 'groups'),
                      }}
                    >
                      {importStatus[school.orgNumber].groups.diff ?? '—'}
                    </ButtonMini>
                  </td>
                  <td class="border-0 text-center py-2 small"></td>
                </tr>

                <!-- Users -->
                <tr class="border-0">
                  <td class="border-0 py-2">
                    <div class="d-flex align-items-center">
                      <pkt-icon name="person" size="16" class="me-2 text-muted"></pkt-icon>
                      <span class="small">Brukere</span>
                    </div>
                  </td>
                  <td class="border-0 text-center py-2 small">
                    <span
                      title={`Sist hentet: ${formatDateTime(importStatus[school.orgNumber].users.fetchedAt)}`}
                    >
                      {importStatus[school.orgNumber].users.fetchedCount ?? '—'}
                    </span>
                  </td>
                  <td class="border-0 text-center py-2 small">
                    {importStatus[school.orgNumber].users.dbCount ?? '—'}
                  </td>
                  <td class="border-0 text-center py-2 small">
                    <ButtonMini
                      options={{
                        title: 'Sjekk import',
                        iconName: 'arrow-circle',
                        skin: 'primary',
                        variant: 'icon-left',
                        onClick: () => handleUpdateEstimate(school.orgNumber, 'users'),
                      }}
                    >
                      {importStatus[school.orgNumber].users.diff ?? '—'}
                    </ButtonMini>
                  </td>
                  <td class="border-0 text-center py-2 small"></td>
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
                    <span
                      title={`Sist hentet: ${formatDateTime(importStatus[school.orgNumber].memberships.fetchedAt)}`}
                    >
                      {importStatus[school.orgNumber].memberships.fetchedCount ?? '—'}
                    </span>
                  </td>
                  <td class="border-0 text-center py-2 small">
                    {importStatus[school.orgNumber].memberships.dbCount ?? '—'}
                  </td>
                  <td class="border-0 text-center py-2 small">
                    <ButtonMini
                      options={{
                        title: 'Sjekk import',
                        iconName: 'arrow-circle',
                        skin: 'primary',
                        variant: 'icon-left',
                        onClick: () => handleUpdateEstimate(school.orgNumber, 'memberships'),
                      }}
                    >
                      {importStatus[school.orgNumber].memberships.diff ?? '—'}
                    </ButtonMini>
                  </td>
                  <td class="border-0 text-center py-2 small"></td>
                </tr>
              </tbody>
            </table>
          </div>

          {#if importStatus[school.orgNumber].lastImportAt}
            <div class="d-flex align-items-center mt-3 pt-3 border-top">
              <pkt-icon name="clock" size="16" class="me-2 text-muted"></pkt-icon>
              <span class="text-muted small">
                Sist import: {formatDateTime(importStatus[school.orgNumber].lastImportAt)}
              </span>
            </div>
          {/if}
        {/if}

        <div>
          <!-- Request fetch job, feide to file -->
          <ButtonMini
            options={{
              title: 'Hent grupper og brukere fra Feide',
              iconName: 'group',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchUsersAndGroups(school.orgNumber),
            }}
          >
            Hent grupper fra Feide
          </ButtonMini>

          <!-- Request import job, file to database -->
          <ButtonMini
            options={{
              title: 'Importér grupper og brukere til databasen',
              iconName: 'download',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleImportGroupsAndUsers(school.orgNumber),
            }}
          >
            Importér til database
          </ButtonMini>

          <!-- Cleanerbot -->
          <ButtonMini
            options={{
              title: 'Aktivér cleanerbot',
              iconName: 'obstacle',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleActivateCleanerBotForSchool(school.orgNumber),
            }}
          >
            Aktivér cleanerbot
          </ButtonMini>
        </div>
      </div>
    </div>
  {/each}
</section>

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isEstimateContainerOpen}
  ariaLabel="Estimat for import"
  onClosed={() => {
    currentEstimate = null
  }}
>
  {#if currentEstimate}
    <ImportEstimate data={currentEstimate} />
  {:else}
    <div class="spinner-border centered" style="width: 10rem; height: 10rem;" role="status">
      <span class="visually-hidden">Laster...</span>
    </div>
  {/if}
</Offcanvas>

<style>
  .timestamp {
    background-color: var(--pkt-color-grays-gray-200);
    padding: 0.1rem 0.2rem;
  }
  .centered {
    position: absolute;
    top: 50%;
    left: 50%;
  }
</style>
