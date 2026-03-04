<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type SchoolType } from '../../generated/types.gen'
  import {
    fetchGroupsAndUsers,
    fetchSchoolImportStatus,
    importGroupsAndUsers,
    schoolsPartialUpdate,
    updateDataIntegrity,
    estimateGroupsImport,
    estimateUsersImport,
    estimateMembershipsImport,
    estimateCleanup,
    schoolsRetrieve,
  } from '../../generated/sdk.gen'
  import type { SchoolImportStatus } from '../../types/models'
  import { formatDateTime, formatDateDistance } from '../../utils/functions'
  import {
    SUBJECTS_ALLOWED_ALL,
    SUBJECTS_ALLOWED_CUSTOM,
    SUBJECTS_ALLOWED_FEIDE,
  } from '../../utils/constants'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import { addAlert } from '../../stores/alerts'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import ImportEstimate from '../../components/ImportEstimate.svelte'
  import CleanerbotEstimate from '../../components/CleanerbotEstimate.svelte'

  type SubjectsAllowed = 'only-custom' | 'only-feide' | 'all'

  interface CleanerbotData {
    orgNumber: string
    changes: {
      group: { 'soft-deleted': any[]; 'hard-deleted': any[] }
      user: { 'soft-deleted': any[]; 'hard-deleted': any[] }
      userGroup: { 'soft-deleted': any[]; 'hard-deleted': any[] }
      goal: { 'soft-deleted': any[]; 'hard-deleted': any[] }
      observation: { 'soft-deleted': any[]; 'hard-deleted': any[] }
    }
    errors: string[]
  }

  const router = useTinyRouter()

  const { schoolId } = $props<{ schoolId: string }>()

  let school = $state<SchoolType>()
  let importDataEstimate = $state<Record<string, any> | null>(null)
  let cleanerbotDataEstimate = $state<CleanerbotData | null>(null)
  let isEstimateContainerOpen = $state<boolean>(false)
  let importTimeline = $state<Record<string, string | undefined>[]>([])

  // Radio options for subject config
  const subjectOptions = [
    { value: SUBJECTS_ALLOWED_ALL, label: 'Alle fag' },
    { value: SUBJECTS_ALLOWED_FEIDE, label: 'Kun fag via Feide-grupper' },
    { value: SUBJECTS_ALLOWED_CUSTOM, label: 'Kun egendefinerte fag' },
  ] as const

  let importStatus = $state<SchoolImportStatus | undefined>(undefined)

  const loadImportStatusForSchool = async () => {
    if (!school) return
    try {
      const result = await fetchSchoolImportStatus({
        path: { orgNumber: school.orgNumber },
      })

      if (result.response.status === 200 && result.data) {
        const data = result.data as SchoolImportStatus
        const { groups, users, memberships, lastImportAt, lastCleanupAt } = data
        importStatus = {
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
          lastCleanupAt: lastCleanupAt,
        }
        importTimeline = [
          {
            type: 'fetch',
            label: 'Last fetch',
            timestamp: groups?.fetchedAt || users?.fetchedAt || memberships?.fetchedAt,
          },
          {
            type: 'import',
            label: 'Last import',
            timestamp: lastImportAt,
          },
          {
            type: 'cleanup',
            label: 'Last cleanup',
            timestamp: lastCleanupAt,
          },
        ].sort((a, b) => {
          const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0
          const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0
          return timeA - timeB
        })
      }
    } catch (error) {
      addAlert({
        type: 'danger',
        message: `Feil ved henting av importstatus for skole ${school.orgNumber}`,
      })
    }
  }

  const fetchSchool = async () => {
    try {
      const result = await schoolsRetrieve({ path: { id: schoolId } })
      school = result.data
      if (school) {
        await loadImportStatusForSchool()
      }
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av skole',
      })
    }
  }

  const handleUpdateImportEstimate = async (dataType: string) => {
    if (!school) return
    isEstimateContainerOpen = true
    let result = null
    if (dataType === 'groups') {
      result = await estimateGroupsImport({ path: { orgNumber: school.orgNumber } })
    } else if (dataType === 'users') {
      result = await estimateUsersImport({ path: { orgNumber: school.orgNumber } })
    } else if (dataType === 'memberships') {
      result = await estimateMembershipsImport({ path: { orgNumber: school.orgNumber } })
    }
    importDataEstimate = result?.data || null
  }

  const handleUpdateCleanerbotEstimate = async (dataType: string) => {
    if (!school) return
    isEstimateContainerOpen = true
    const result = await estimateCleanup({ path: { orgNumber: school.orgNumber } })
    cleanerbotDataEstimate = (result?.data as CleanerbotData) ?? null
  }

  const toggleServiceEnabled = async () => {
    if (!school) return
    try {
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isServiceEnabled: !school.isServiceEnabled },
      })
      await fetchSchool()
    } catch (error) {
      addAlert({
        type: 'danger',
        message: `Feil ved oppdatering av status for skole ${school.displayName}`,
      })
    }
  }

  const toggleServiceEnabledForStudents = async () => {
    if (!school) return
    try {
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isServiceEnabledForStudents: !school.isServiceEnabledForStudents },
      })
      await fetchSchool()
    } catch (error) {
      addAlert({
        type: 'danger',
        message: `Feil ved oppdatering av elev-tilgang for skole ${school.displayName}`,
      })
    }
  }

  // Toggle whether group goals can be created at the school
  const toggleGroupGoalEnabled = async () => {
    if (!school) return
    try {
      const current = school.isGroupGoalEnabled ?? false
      const result = await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isGroupGoalEnabled: !current },
      })
      await fetchSchool()
    } catch (error) {
      console.error('Error updating isGroupGoalEnabled:', error)
    }
  }

  // Toggle whether statuses can be created at the school
  const toggleStatusEnabled = async () => {
    if (!school) return
    try {
      const current = Boolean(school.isStatusEnabled)
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isStatusEnabled: !current },
      })
      await fetchSchool()
    } catch (error) {
      console.error('Error updating isStatusEnabled:', error)
    }
  }

  // Toggle whether group title is displayed in goal edit
  const toggleGoalTitleEnabled = async () => {
    if (!school) return
    try {
      const current = Boolean(school.isGoalTitleEnabled)
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isGoalTitleEnabled: !current },
      })
      await fetchSchool()
    } catch (error) {
      console.error('Error updating isGoalTitleEnabled:', error)
    }
  }

  // Toggle whether teachers can see the students list menu item
  const toggleStudentListEnabled = async () => {
    if (!school) return
    try {
      const current = Boolean(school.isStudentListEnabled)
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { isStudentListEnabled: !current },
      })
      await fetchSchool()
    } catch (error) {
      console.error('Error updating isStudentListEnabled:', error)
    }
  }

  const updateSubjectsAllowed = async (value: SubjectsAllowed) => {
    if (!school) return
    if (school.subjectsAllowed === value) return
    try {
      await schoolsPartialUpdate({
        path: { id: school.id },
        body: { subjectsAllowed: value },
      })
      await fetchSchool()
    } catch (error) {
      console.error('Error updating subjectsAllowed:', error)
    }
  }

  const handleActivateCleanerBotForSchool = async () => {
    if (!school) return
    const orgNumber = school.orgNumber
    const confirmed = confirm(`Er du helt sikker på at du vil kjøre ryddejobb for ${orgNumber}?`)

    if (!confirmed) return
    try {
      const result = await updateDataIntegrity({
        path: { orgNumber: orgNumber },
      })

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for sletting av snargh for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks/?back=/admin/schools/' + school.id)
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

  const handleFetchUsersAndGroups = async () => {
    if (!school) return
    const orgNumber = school.orgNumber

    try {
      const result = await fetchGroupsAndUsers({
        path: { orgNumber: orgNumber },
      })

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Opprettet bakgrunnsjobber for henting av grupper og brukere for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks/?back=/admin/schools/' + school.id)
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

  const handleImportGroupsAndUsers = async () => {
    if (!school) return
    const orgNumber = school.orgNumber

    try {
      const result = await importGroupsAndUsers({
        path: { orgNumber: orgNumber },
      })

      if (result.response.status === 201) {
        addAlert({
          type: 'success',
          message: `Bakgrunnsjobb opprettet for import av grupper og brukere for ${orgNumber}`,
        })
        router.navigate('/admin/data-maintenance-tasks/?back=/admin/schools/' + school.id)
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
    fetchSchool()
  })
</script>

<div class="container py-3">
  {#if school}
    <div class="p-4" class:opacity-25={!school.isServiceEnabled}>
      <div class="d-flex align-items-center">
        <h2>{school.displayName}</h2>
        <pkt-checkbox
          id={'service-' + school.id}
          class="ms-auto"
          label={school.isServiceEnabled ? 'Aktivert' : 'Deaktivert'}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isServiceEnabled}
          checked={school.isServiceEnabled}
          onchange={() => toggleServiceEnabled()}
        ></pkt-checkbox>
      </div>

      <div class="text-muted small">
        {school.orgNumber}
      </div>
      <div class="text-muted small">
        Sist oppdatert {formatDateTime(school.updatedAt)}
      </div>

      <!-- Subjects -->
      <section class="border border-3 p-3 my-3">
        <h3 class="mb-3">Fag</h3>
        <p class="mb-3">Hvilke fag er tilgjengelige på skolen?</p>
        <fieldset class="d-flex flex-wrap gap-4">
          <legend class="visually-hidden">Velg hvilke fag som er tilgjengelige på skolen</legend>
          {#each subjectOptions as option}
            <pkt-radiobutton
              name={'subjectsAllowed-' + school.id}
              value={option.value}
              label={option.label}
              checked={school.subjectsAllowed === option.value}
              onchange={() => updateSubjectsAllowed(option.value)}
            ></pkt-radiobutton>
          {/each}
        </fieldset>
      </section>

      <!-- Groups -->
      <section class="border border-3 p-3 my-3">
        <h3 class="mb-3">Grupper</h3>
        <pkt-checkbox
          id={'group-goal-' + school.id}
          label={`Gruppemål ${school.isGroupGoalEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isGroupGoalEnabled}
          checked={school.isGroupGoalEnabled}
          onchange={() => toggleGroupGoalEnabled()}
        ></pkt-checkbox>

        <pkt-checkbox
          id={'goal-title' + school.id}
          class="ms-1"
          label={`Fritekst-tittel på mål ${school.isGoalTitleEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isGoalTitleEnabled}
          checked={school.isGoalTitleEnabled}
          onchange={() => toggleGoalTitleEnabled()}
        ></pkt-checkbox>
      </section>

      <!-- Status -->
      <section class="border border-3 p-3 my-3">
        <h3 class="mb-3">Status</h3>
        <pkt-checkbox
          id={'status-' + school.id}
          label={`Status ${school.isStatusEnabled ? '' : 'IKKE'} tilgjengelig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isStatusEnabled}
          checked={school.isStatusEnabled}
          onchange={() => toggleStatusEnabled()}
        ></pkt-checkbox>
      </section>

      <!-- Teacher navigation -->
      <section class="border border-3 p-3 my-3">
        <h3 class="mb-3">Navigasjon for lærere</h3>
        <pkt-checkbox
          id={'student-list-' + school.id}
          label={`Elevliste ${school.isStudentListEnabled ? '' : 'IKKE'} synlig`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isStudentListEnabled}
          checked={school.isStudentListEnabled}
          onchange={() => toggleStudentListEnabled()}
        ></pkt-checkbox>
      </section>

      <!-- Student access -->
      <section
        class="border border-3 p-3 my-3"
        title="Skrudd av i påvente av diskusjon rundt elev-tilgang"
      >
        <h3 class="mb-3">Tilgang for elever</h3>
        <pkt-checkbox
          id={'student-access-' + school.id}
          label={`Elever har ${school.isServiceEnabledForStudents ? '' : 'IKKE'} tilgang til tjenesten`}
          labelPosition="right"
          isSwitch="true"
          aria-checked={school.isServiceEnabledForStudents}
          checked={school.isServiceEnabledForStudents}
          onchange={() => toggleServiceEnabledForStudents()}
          disabled={true}
        ></pkt-checkbox>
      </section>

      <!-- Data import stuff -->
      <section class="border border-3 p-3 my-3">
        <h3 class="mb-3">Data maintenance</h3>

        <div class="mb-3">
          <!-- Request fetch job, feide to file -->
          <ButtonMini
            options={{
              title: 'Fetch users and groups Feide',
              iconName: 'download',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleFetchUsersAndGroups(),
            }}
          >
            Fetch from Feide
          </ButtonMini>

          <!-- Request import job, file to database -->
          <ButtonMini
            options={{
              title: 'Import groups and users to database',
              iconName: 'process-iteration',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleImportGroupsAndUsers(),
            }}
          >
            Import to database
          </ButtonMini>

          <!-- Cleanerbot -->
          <ButtonMini
            options={{
              title: 'Activate cleanerbot for school',
              iconName: 'cupboard',
              skin: 'secondary',
              variant: 'icon-left',
              onClick: () => handleActivateCleanerBotForSchool(),
            }}
          >
            Run cleanerbot
          </ButtonMini>
        </div>

        <hr class="border border-3 opacity-50" />

        {#if importStatus}
          <h4 class="mt-4 mb-3">Latest events</h4>
          <table class="table mb-2">
            <thead>
              <tr class="border-bottom">
                {#each importTimeline as event}
                  <th>{event.label}</th>
                {/each}
              </tr>
            </thead>
            <tbody>
              <tr>
                {#each importTimeline as event, index}
                  <td class="border-0 py-2 small">
                    {event.timestamp ? formatDateTime(event.timestamp) : '—'}
                    <br />
                    <span class="text-muted">
                      {#if index > 0}
                        {formatDateDistance(importTimeline[index - 1].timestamp, event.timestamp)} etter
                        {importTimeline[index - 1].type}
                      {:else}
                        {formatDateDistance(event.timestamp)}
                      {/if}
                    </span>
                  </td>
                {/each}
              </tr>
            </tbody>
          </table>

          <hr class="border border-3 opacity-50" />

          <h4 class="mt-4 mb-3">Data insight</h4>
          <table class="table table-sm align-middle mt-4">
            <thead>
              <tr class="border-bottom">
                <th>Type</th>
                <th class="text-center">Fetched</th>
                <th class="text-center">Database</th>
                <th
                  class="text-center"
                  title="Note: Even if this number is zero, there can still be a diff!"
                >
                  Fetch vs DB
                </th>
                <th class="text-center" title="What will happen if the import runs?">
                  WWHI:Import
                </th>
                <th class="text-center" title="What will happen if the cleanerbot runs?">
                  WWHI:Cleanerbot
                </th>
              </tr>
            </thead>

            <tbody>
              <!-- Groups -->
              <tr class="border-0">
                <td class="border-0 py-2">
                  <div class="d-flex align-items-center">
                    <pkt-icon name="group" size="16" class="me-2 text-muted"></pkt-icon>
                    <span class="small">Groups</span>
                  </div>
                </td>
                <td class="border-0 text-center py-2 small">
                  <span title={`Sist hentet: ${formatDateTime(importStatus.groups.fetchedAt)}`}>
                    {importStatus.groups.fetchedCount ?? '—'}
                  </span>
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.groups.dbCount ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.groups.diff ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  <ButtonMini
                    options={{
                      title: 'Sjekk import',
                      iconName: 'arrow-circle',
                      skin: 'secondary',
                      variant: 'icon-left',
                      onClick: () => handleUpdateImportEstimate('groups'),
                    }}
                  >
                    Check
                  </ButtonMini>
                </td>
                <td class="border-0 text-center py-2 small" rowspan="3">
                  <ButtonMini
                    options={{
                      title: 'Check cleanup estimate',
                      iconName: 'arrow-circle',
                      skin: 'secondary',
                      variant: 'icon-left',
                      onClick: () => handleUpdateCleanerbotEstimate('cleanup'),
                    }}
                  >
                    Check
                  </ButtonMini>
                </td>
              </tr>

              <!-- Users -->
              <tr class="border-0">
                <td class="border-0 py-2">
                  <div class="d-flex align-items-center">
                    <pkt-icon name="person" size="16" class="me-2 text-muted"></pkt-icon>
                    <span class="small">Users (teachers & students)</span>
                  </div>
                </td>
                <td class="border-0 text-center py-2 small">
                  <span title={`Sist hentet: ${formatDateTime(importStatus.users.fetchedAt)}`}>
                    {importStatus.users.fetchedCount ?? '—'}
                  </span>
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.users.dbCount ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.users.diff ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  <ButtonMini
                    options={{
                      title: 'Sjekk import',
                      iconName: 'arrow-circle',
                      skin: 'secondary',
                      variant: 'icon-left',
                      onClick: () => handleUpdateImportEstimate('users'),
                    }}
                  >
                    Check
                  </ButtonMini>
                </td>
              </tr>

              <!-- Memberships -->
              <tr class="border-0">
                <td class="border-0 py-2">
                  <div class="d-flex align-items-center">
                    <pkt-icon name="holding-hands" size="16" class="me-2 text-muted"></pkt-icon>
                    <span class="small">Memberships</span>
                  </div>
                </td>
                <td class="border-0 text-center py-2 small">
                  <span
                    title={`Sist hentet: ${formatDateTime(importStatus.memberships.fetchedAt)}`}
                  >
                    {importStatus.memberships.fetchedCount ?? '—'}
                  </span>
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.memberships.dbCount ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  {importStatus.memberships.diff ?? '—'}
                </td>
                <td class="border-0 text-center py-2 small">
                  <ButtonMini
                    options={{
                      title: 'Sjekk import',
                      iconName: 'arrow-circle',
                      skin: 'secondary',
                      variant: 'icon-left',
                      onClick: () => handleUpdateImportEstimate('memberships'),
                    }}
                  >
                    Check
                  </ButtonMini>
                </td>
              </tr>
            </tbody>
          </table>
        {/if}
      </section>
    </div>
  {:else}
    <div class="d-flex flex-column align-items-center py-5">
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Laster...</span>
      </div>
      <div class="text-muted mt-3">Laster skoleinformasjon...</div>
    </div>
  {/if}
</div>

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isEstimateContainerOpen}
  ariaLabel="Estimat for import"
  width={'70vw'}
  onClosed={() => {
    importDataEstimate = null
  }}
>
  {#if importDataEstimate}
    <ImportEstimate
      data={importDataEstimate}
      onDone={() => {
        isEstimateContainerOpen = false
      }}
    />
  {:else if cleanerbotDataEstimate}
    <CleanerbotEstimate
      data={cleanerbotDataEstimate}
      onDone={() => {
        isEstimateContainerOpen = false
      }}
    />
  {:else}
    <div class="spinner-border centered" style="width: 10rem; height: 10rem;" role="status">
      <span class="visually-hidden">Laster...</span>
    </div>
  {/if}
</Offcanvas>

<style>
  .centered {
    position: absolute;
    top: 40%;
    left: 40%;
  }
</style>
