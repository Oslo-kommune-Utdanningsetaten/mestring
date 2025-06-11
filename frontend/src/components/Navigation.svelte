<script lang="ts">
  import Link from './Link.svelte'
  import oslologoUrl from '@oslokommune/punkt-assets/dist/logos/oslologo.svg?url'

  import { currentPath } from '../stores/navigation'
  import { dataStore, setCurrentSchool } from '../stores/data'
  import { type SchoolReadable } from '../generated/types.gen'
  import { schoolsList } from '../generated/sdk.gen'
  import { apiHealth } from '../stores/apiHealth'

  let isHomeActive = $derived($currentPath === '/')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isAboutActive = $derived($currentPath.startsWith('/about'))
  let isSchoolsActive = $derived($currentPath.startsWith('/schools'))

  let schools = $state<SchoolReadable[]>([])

  async function fetchSchools() {
    try {
      const result = await schoolsList({
        query: {
          isServiceEnabled: true,
        },
      })
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  function handleSetCurrentSchool(schoolId: string) {
    const selectedSchool = schools.find(s => s.id === schoolId)
    if (!selectedSchool) {
      console.error('Selected school not found')
      return
    }
    setCurrentSchool(selectedSchool)
  }

  $effect(() => {
    fetchSchools()
    // Check API health on component load
    apiHealth.checkHealth()

    // Set up an interval to check API health periodically (every 30 seconds)
    const interval = setInterval(() => {
      apiHealth.checkHealth()
    }, 30000)

    return () => {
      clearInterval(interval)
    }
  })
</script>

{#if !$apiHealth.isOk}
  <div class="alert alert-danger">
    <strong>Not all is well😬</strong>
    API: {$apiHealth.api} | DB: {$apiHealth.db}
  </div>
{/if}

<nav class="navbar navbar-expand-md navbar-light bg-light">
  <div class="container-md">
    <a class="navbar-brand fw-bold" href="/">
      {$dataStore.currentSchool ? $dataStore.currentSchool.displayName : 'INGEN SKOLE VALGT'}
    </a>
    <ul class="navbar-nav ms-auto">
      <li class="nav-item">
        <Link to="/" className={`nav-link ${isHomeActive ? 'active' : ''}`}>Hjem</Link>
      </li>
      <li class="nav-item">
        <Link to="/students" className={`nav-link ${isStudentsActive ? 'active' : ''}`}>
          Elever
        </Link>
      </li>
      <li class="nav-item">
        <Link to="/schools" className={`nav-link ${isSchoolsActive ? 'active' : ''}`}>Skoler</Link>
      </li>
      <li class="nav-item">
        <Link to="/about" className={`nav-link ${isAboutActive ? 'active' : ''}`}>
          Om tjenesten
        </Link>
      </li>
      <li class="nav-item dropdown">
        <a
          class="nav-link dropdown-toggle"
          id="navbarDropdown"
          role="button"
          data-bs-toggle="dropdown"
        >
          Admin
        </a>
        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
          {#each schools as school}
            <li>
              <a
                class="dropdown-item {$dataStore.currentSchool?.id === school.id
                  ? 'selected-school'
                  : ''}"
                href="#"
                onclick={() => handleSetCurrentSchool(school.id)}
              >
                {school.displayName}
              </a>
            </li>
          {/each}
          <li><hr class="dropdown-divider" /></li>
          <li><a class="dropdown-item" href="#">Option 3</a></li>
        </ul>
      </li>
    </ul>
    <a href="https://www.oslo.kommune.no" class="logo-image" target="_blank">
      <img class="oslologo" alt="Oslo kommune logo" src={oslologoUrl} />
    </a>
  </div>
</nav>

<style>
  .logo-image {
    width: 100px;
    padding-left: 30px;
  }

  .selected-school {
    background-color: #f8f9fa;
    color: #000;
    font-weight: bold;
  }
</style>
