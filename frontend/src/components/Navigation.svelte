<script lang="ts">
  import Link from './Link.svelte'
  import osloLogo from '../assets/oslo_logo_sort.svg'
  import { currentPath } from '../stores/navigation'
  import { dataStore, setCurrentSchool } from '../stores/data'
  import { type SchoolReadable } from '../api/types.gen'
  import { schoolsList, schoolsPartialUpdate } from '../api/sdk.gen'

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
    console.log('Current path changed:', $currentPath)
    fetchSchools()
  })
</script>

<nav class="navbar navbar-expand-md navbar-light bg-light">
  <div class="container-md">
    <a class="navbar-brand" href="/">
      Mestring: {$dataStore.currentSchool
        ? $dataStore.currentSchool.displayName
        : 'INGEN SKOLE VALGT'}
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
              <a class="dropdown-item" href="#" onclick={() => handleSetCurrentSchool(school.id)}>
                {$dataStore.currentSchool?.id === school.id ? '✅' : ''}
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
      <img alt="Oslo Kommune logo" src={osloLogo} />
    </a>
  </div>
</nav>

<style>
  .logo-image {
    width: 100px;
    padding-left: 30px;
  }
</style>
