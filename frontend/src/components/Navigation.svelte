<script lang="ts">
  import { dataStore, currentUser } from '../stores/data'
  import { login, logout } from '../stores/auth'
  import { currentPath } from '../stores/navigation'

  import Link from './Link.svelte'
  import GoalIconCelebration from './GoalIconCelebration.svelte'
  import oslologoUrl from '@oslokommune/punkt-assets/dist/logos/oslologo.svg?url'

  let currentSchool = $derived($dataStore.currentSchool)
  let isHomeActive = $derived($currentPath === '/')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isAboutActive = $derived($currentPath === '/about')
  let isAdminActive = $derived($currentPath.startsWith('/admin'))
  let isProfileActive = $derived($currentPath.startsWith('/profile'))
  let environmentWarning = $derived(
    window.location.hostname.includes('mestring-dev')
      ? 'development'
      : window.location.hostname.includes('localhost')
        ? 'localhost'
        : undefined
  )
</script>

<nav class="navbar navbar-expand-md navbar-light bg-light">
  {#if environmentWarning}
    <div
      class="environment-warning-banner"
      title="Du bruker en ikke-produksjonsversjon av applikasjonen"
    >
      {environmentWarning}
    </div>
  {/if}
  <div class="container-md">
    <Link className="navbar-brand" to="/">
      <span class="me-1 goal-icon-wrapper">
        <pkt-icon name="goal" title="Mestring logo" aria-hidden="true"></pkt-icon>
        <span class="celebration-overlay" aria-hidden="true">
          <GoalIconCelebration />
        </span>
      </span>
      <h1>{currentSchool?.displayName || 'INGEN SKOLE VALGT'}</h1>
    </Link>

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
          {#if currentSchool?.isStudentListEnabled || $dataStore.hasUserAccessToPath('/students')}
            <li class="nav-item">
              <Link to="/students" className={`nav-link ${isStudentsActive ? 'active' : ''}`}>
                Elever
              </Link>
            </li>
          {/if}

          {#if $dataStore.hasUserAccessToPath('/admin')}
            <li class="nav-item dropdown">
              <!-- svelte-ignore a11y_invalid_attribute -->
              <a
                class={`nav-link dropdown-toggle ${isAdminActive ? 'active' : ''}`}
                id="navbarDropdown"
                role="button"
                data-bs-toggle="dropdown"
                href="#"
              >
                Admin
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                <li>
                  <Link to="/admin/schools" className="dropdown-item">Skoler</Link>
                </li>
                <li>
                  <Link to="/admin/groups" className="dropdown-item">Grupper</Link>
                </li>
                <li>
                  <Link to="/admin/subjects" className="dropdown-item">Fag</Link>
                </li>
                <li>
                  <Link to="/admin/users" className="dropdown-item">Brukere</Link>
                </li>
                <li>
                  <Link to="/admin/mastery-schemas" className="dropdown-item">Mastery Schemas</Link>
                </li>
                <li>
                  <Link to="/admin/data-maintenance-tasks" className="dropdown-item">
                    Bakgrunnsjobber
                  </Link>
                </li>
                <li class="ms-3 mt-1">
                  <a href="/analytics/index.php" target="_blank">Analytics</a>
                </li>
              </ul>
            </li>
          {/if}

          {#if $dataStore.hasUserAccessToPath('/profile')}
            <li class="nav-item dropdown" title="Logget på som {$currentUser.name}">
              <a
                class={`nav-link dropdown-toggle ${isProfileActive ? 'active' : ''}`}
                id="navbarDropdown"
                role="button"
                data-bs-toggle="dropdown"
                href="#"
              >
                Profil
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                <li><Link to="/profile" className="dropdown-item">Min side</Link></li>
                <li>
                  <Link to="/" className="dropdown-item" onclick={logout}>Logg ut</Link>
                </li>
              </ul>
            </li>
          {/if}
        {/if}

        {#if !$currentUser}
          <li class="nav-item">
            <a class="nav-link" href="#" onclick={login}>Logg inn</a>
          </li>
        {/if}
      </ul>

      <!-- Logo outside collapsible area for desktop -->
      <a href="https://www.oslo.kommune.no" class="logo-image ms-3" target="_blank">
        <img class="oslologo" alt="Oslo kommune logo" src={oslologoUrl} />
      </a>
    </div>
  </div>
</nav>

<style>
  h1 {
    font-size: 1.8rem;
    display: inline-block;
    padding-left: 0.5em;
  }

  .logo-image {
    display: inline-block;
    width: 100px;
    max-width: 100px;
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

  nav.navbar {
    position: relative;
  }

  .environment-warning-banner {
    position: absolute;
    top: 26px;
    left: -40px;
    z-index: 5;
    display: inline-block;
    width: 170px;
    padding: 5px 0;
    background: #d63384;
    color: #fff;
    font-family: 'courier new', courier, monospace;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.12em;
    text-align: center;
    text-transform: uppercase;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.18);
    transform: rotate(-45deg);
    pointer-events: none;
  }
</style>
