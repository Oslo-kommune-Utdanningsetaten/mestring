<script lang="ts">
  import Link from './Link.svelte'
  import GoalIconCelebration from './GoalIconCelebration.svelte'
  import oslologoUrl from '@oslokommune/punkt-assets/dist/logos/oslologo.svg?url'

  import { currentPath } from '../stores/navigation'
  import { dataStore, currentUser } from '../stores/data'
  import { apiHealth } from '../stores/apiHealth'
  import { login, logout } from '../stores/auth'

  let currentSchool = $derived($dataStore.currentSchool)
  let isHomeActive = $derived($currentPath === '/')
  let isAboutActive = $derived($currentPath === '/about')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  const API_CHECK_INTERVAL = 60 * 1000 // every 60 secondss

  $effect(() => {
    // Check API health on component load
    apiHealth.checkHealth()

    // Interval to check API health periodically
    const interval = setInterval(() => {
      apiHealth.checkHealth()
    }, API_CHECK_INTERVAL)

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
      <span class="me-1 goal-icon-wrapper">
        <pkt-icon name="goal"></pkt-icon>
        <span class="celebration-overlay">
          <GoalIconCelebration />
        </span>
      </span>
      {currentSchool?.displayName || 'INGEN SKOLE VALGT'}
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
        {#if $currentUser}
          <li class="nav-item">
            <Link to="/" className={`nav-link ${isHomeActive ? 'active' : ''}`}>Hjem</Link>
          </li>
          {#if $dataStore.isSchooladmin || $dataStore.isSuperadmin || currentSchool?.isStudentListEnabled}
            <li class="nav-item">
              <Link to="/students" className={`nav-link ${isStudentsActive ? 'active' : ''}`}>
                Elever
              </Link>
            </li>
          {/if}
        {/if}
        <li class="nav-item">
          <Link to="/about" className={`nav-link ${isAboutActive ? 'active' : ''}`}>
            Om&nbsp;tjenesten
          </Link>
        </li>

        {#if $currentUser?.isSuperadmin}
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
              <li>
                <Link to="/admin/schools" className="dropdown-item">Skoler</Link>
              </li>
              <li>
                <Link to="/admin/users" className="dropdown-item">Brukere</Link>
              </li>
              <li>
                <Link to="/admin/subjects" className="dropdown-item">Fag</Link>
              </li>
              <li>
                <Link to="/admin/groups" className="dropdown-item">Grupper</Link>
              </li>
              <li>
                <Link to="/admin/data-maintenance-tasks" className="dropdown-item">
                  Bakgrunnsjobber
                </Link>
              </li>
              <li>
                <Link to="/admin/mastery-schemas" className="dropdown-item">Mastery Schemas</Link>
              </li>
            </ul>
          </li>
        {/if}

        {#if $currentUser}
          <li class="nav-item dropdown" title="Logget på som {$currentUser.name}">
            <a
              class="nav-link dropdown-toggle"
              id="navbarDropdown"
              role="button"
              data-bs-toggle="dropdown"
            >
              Profil
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
              <li><a class="dropdown-item" href="/user-info">Min side</a></li>
              <li>
                <a class="dropdown-item" href="#" onclick={logout}>Logg ut</a>
              </li>
            </ul>
          </li>
        {/if}

        {#if !$currentUser}
          <li class="nav-item">
            <a class="nav-link" href="#" onclick={login}>Logg inn</a>
          </li>
        {/if}
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

  .goal-icon-wrapper {
    position: relative;
    display: inline-flex;
    width: 28px;
    aspect-ratio: 1 / 1;
  }

  .goal-icon-wrapper :global(pkt-icon) {
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .goal-icon-wrapper .celebration-overlay {
    position: absolute;
    inset: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
</style>
