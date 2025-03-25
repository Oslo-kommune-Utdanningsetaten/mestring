<script lang="ts">
  import Link from './Link.svelte'
  import osloLogo from '../assets/oslo_logo_sort.svg'
  import { currentPath } from '../stores/navigation'

  // Using Svelte 5 runes for reactive states
  let isHomeActive = $derived($currentPath === '/')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isSubjectsActive = $derived($currentPath.startsWith('/subjects'))
  let isAboutActive = $derived($currentPath.startsWith('/about'))

  $effect(() => {
    console.log('Current path changed:', $currentPath)
  })

  // Toggle for responsive menu
  let isNavExpanded = false
  const toggleNav = () => {
    isNavExpanded = !isNavExpanded
  }
</script>

<nav class="navbar navbar-expand-md navbar-light bg-light">
  <div class="container-md">
    <a class="navbar-brand" href="/">Vurdering på Haukåsen</a>

    <button
      class="navbar-toggler"
      type="button"
      on:click={toggleNav}
      aria-expanded={isNavExpanded}
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse {isNavExpanded ? 'show' : ''}" id="navbarNav">
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
          <Link to="/subjects" className={`nav-link ${isSubjectsActive ? 'active' : ''}`}>Fag</Link>
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
            Options
          </a>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
            <li><a class="dropdown-item" href="#">Option 1</a></li>
            <li><a class="dropdown-item" href="#">Option 2</a></li>
            <li><hr class="dropdown-divider" /></li>
            <li><a class="dropdown-item" href="#">Option 3</a></li>
          </ul>
        </li>
      </ul>
      <a href="https://www.oslo.kommune.no" class="logo-image" target="_blank">
        <img alt="Oslo Kommune logo" src={osloLogo} />
      </a>
    </div>
  </div>
</nav>

<style>
  .logo-image {
    width: 100px;
    padding-left: 30px;
  }
</style>
