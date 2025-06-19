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
  let isSchoolsActive = $derived($currentPath.startsWith('/schools'))

  let schools = $state<SchoolReadable[]>([])

  const fetchSchools = async () => {
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

  const handleSetCurrentSchool = async (schoolId: string) => {
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

    // Set up an interval to check API health periodically (every 60 seconds)
    const interval = setInterval(() => {
      apiHealth.checkHealth()
    }, 60 * 1000)

    return () => {
      clearInterval(interval)
    }
  })
</script>

{#if !$apiHealth.isOk}
  <div class="alert alert-danger">
    <strong>Connection issues 😬</strong>
    API: {$apiHealth.api} | DB: {$apiHealth.db}
  </div>
{/if}

<nav class="navbar navbar-expand-md navbar-light bg-light">
  <div class="container-md">
    <a class="navbar-brand fw-bold" href="/">
      {$dataStore.currentSchool ? $dataStore.currentSchool.displayName : 'INGEN SKOLE VALGT'}
    </a>

    <!-- Burger menu button -->
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
      aria-controls="navbarNav"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <!-- Collapsible content -->
    <div class="collapse navbar-collapse" id="navbarNav">
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
          <Link to="/schools" className={`nav-link ${isSchoolsActive ? 'active' : ''}`}>
            Skoler
          </Link>
        </li>
        <li class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle"
            id="navbarDropdown"
            role="button"
            data-bs-toggle="dropdown"
          >
            Annet
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
            <li><a class="dropdown-item" href="/mastery-schemas">Mastery Schemas</a></li>
            <li><a class="dropdown-item" href="/about">Om&nbsp;tjenesten</a></li>
            <li><a class="dropdown-item" href="#">Option 3</a></li>
          </ul>
        </li>
      </ul>

      <!-- Logo outside collapsible area for desktop -->
      <a href="https://www.oslo.kommune.no" class="logo-image" target="_blank">
        <img class="oslologo" alt="Oslo kommune logo" src={oslologoUrl} />
      </a>
    </div>
  </div>
</nav>

<style>
  .logo-image {
    display: inline-block;
    width: 100px;
    max-width: 100px;
    padding-left: 30px;
  }

  .selected-school {
    background-color: #f8f9fa;
    color: #000;
    font-weight: bold;
  }
</style>
