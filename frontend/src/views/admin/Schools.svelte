<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { type SchoolType } from '../../generated/types.gen'
  import { feideImportSchool, schoolsList, schoolsPartialUpdate } from '../../generated/sdk.gen'
  import { formatDateTime } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import { addAlert } from '../../stores/alerts'
  import { dataStore } from '../../stores/data'
  import Link from '../../components/Link.svelte'

  const router = useTinyRouter()
  let schools = $state<SchoolType[]>([])
  let feideOrgInput: HTMLInputElement

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
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av skoler',
      })
      schools = []
    }
  }

  const handleImportSchool = async (orgNumber: string) => {
    try {
      const result = await feideImportSchool({
        path: { orgNumber },
      })
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

  $effect(() => {
    fetchSchools()
  })
</script>

<section class="container py-3">
  <h2>Alle skoler</h2>

  <!-- Add new school by org number -->
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
          <h3><Link to="/admin/schools/{school.id}">{school.displayName}</Link></h3>
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
      </div>
    </div>
  {/each}
</section>

<style>
</style>
