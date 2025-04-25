<script lang="ts">
  import Link from './Link.svelte'
  import osloLogo from '../assets/oslo_logo_sort.svg'
  import { currentPath } from '../stores/navigation'
  import { dataStore, setCurrentUser } from '../stores/data'

  let isHomeActive = $derived($currentPath === '/')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isAboutActive = $derived($currentPath.startsWith('/about'))
  let isSchoolsActive = $derived($currentPath.startsWith('/schools'))

  const teachers = $derived($dataStore.teachers)

  function handleSetCurrentUser(teacherId: string) {
    const selectedTeacher = teachers.find(t => t.id === teacherId)
    if (!selectedTeacher) {
      console.error('Selected teacher not found')
      return
    }
    const currentUser = {
      id: selectedTeacher.id,
      name: selectedTeacher.name,
      teacherId: selectedTeacher.id,
    }
    setCurrentUser(currentUser)
  }

  $effect(() => {
    console.log('Current path changed:', $currentPath)
  })
</script>

<nav class="navbar navbar-expand-md navbar-light bg-light">
  <div class="container-md">
    <a class="navbar-brand" href="/">Vurdering på Haukåsen</a>
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
          href="#"
          id="navbarDropdown"
          role="button"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          {$dataStore.currentUser?.name || 'options'}
        </a>
        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
          {#each teachers as teacher}
            <li>
              <a class="dropdown-item" href="#" onclick={() => handleSetCurrentUser(teacher.id)}>
                {teacher.name}
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
