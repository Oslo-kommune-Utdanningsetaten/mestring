<script lang="ts">
  import { currentUser, currentSchool } from '../stores/data'
  import { login, logout } from '../stores/auth'
  import { currentPath } from '../stores/navigation'
  import { hasUserAccessToPath } from '../stores/access'
  import oslologoUrl from '@oslokommune/punkt-assets/dist/logos/oslologo.svg?url'
  import { preferredSchoolYear } from '../stores/localStorageFunctions'
  import { getAllSchoolYears, getCurrentSchoolYear } from '../utils/schoolYear'
  import type { SchoolType } from '../generated/types.gen'

  import Link from './Link.svelte'
  import GoalIconCelebration from './GoalIconCelebration.svelte'
  import YearSelector from './YearSelector.svelte'
  import SchoolSelector from './SchoolSelector.svelte'

  const allYearsForCurrentSchool = $derived(
    $currentSchool ? getAllSchoolYears(new Date($currentSchool.createdAt)).reverse() : []
  )

  let isHomeActive = $derived($currentPath === '/')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isSchoolActive = $derived(
    ['students', 'goals', 'groups-compare', 'stats'].includes($currentPath.split('/')[1])
  )
  let isAdminActive = $derived($currentPath.startsWith('/admin'))
  let isProfileActive = $derived($currentPath.startsWith('/profile'))
  let environmentWarning = $derived(
    window.location.hostname.includes('mestring-dev')
      ? 'development'
      : window.location.hostname.includes('localhost')
        ? 'localhost'
        : undefined
  )

  const schools = $derived<SchoolType[]>($currentUser?.schools ?? [])
  const hasMultipleSchools = $derived(!!$currentUser && schools.length > 1)
</script>

{#snippet schoolSelectorDropdown()}
  <div class="dropdown navbar-brand-dropdown">
    <button
      id="navbarDropdownSchoolSelector"
      class="dropdown-toggle dropdown-toggle-split nav-link py-0 ps-0"
      type="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      aria-label="Velg skole"
      title="Velg skole"
    >
      <span class="visually-hidden">Velg skole</span>
    </button>
    <span class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdownSchoolSelector">
      <SchoolSelector />
    </span>
  </div>
{/snippet}

<nav class="navbar navbar-expand-md bg-light">
  {#if environmentWarning}
    <div
      class="environment-warning-banner"
      title="Du bruker en ikke-produksjonsversjon av applikasjonen"
    >
      {environmentWarning}
    </div>
  {/if}

  <div class="container-md">
    <div class="d-flex align-items-center">
      <Link
        className="navbar-brand d-flex align-items-center"
        to={$hasUserAccessToPath('/admin/schools/:schoolId')
          ? `/admin/schools/${$currentSchool?.id}`
          : '/'}
      >
        <!-- Mestring icon -->
        <span class="goal-icon-wrapper me-3">
          <pkt-icon name="goal" title="Mestring logo" aria-hidden="true"></pkt-icon>
          <span class="celebration-overlay" aria-hidden="true">
            <GoalIconCelebration />
          </span>
        </span>

        <h1>{$currentSchool?.displayName || 'INGEN SKOLE VALGT'}</h1>
      </Link>
      {#if hasMultipleSchools}
        {@render schoolSelectorDropdown()}
      {/if}
    </div>

    <!-- Burger menu button, visible on narrow displays -->
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
      <ul class="navbar-nav ms-auto align-items-center">
        {#if currentUser}
          <!-- Home (aka "my groups") -->
          <li class="nav-item">
            <Link to="/" className={`nav-link ${isHomeActive ? 'active' : ''}`}>Hjem</Link>
          </li>

          {#if $currentSchool?.isStudentListEnabled && $hasUserAccessToPath('/students')}
            <li class="nav-item">
              <Link to="/students" className={`nav-link ${isStudentsActive ? 'active' : ''}`}>
                Elever
              </Link>
            </li>
          {/if}

          <!-- School inspector/admin menu -->
          {#if $hasUserAccessToPath('/school')}
            <li class="nav-item dropdown">
              <!-- svelte-ignore a11y_invalid_attribute -->
              <a
                class={'nav-link dropdown-toggle'}
                class:active={isSchoolActive}
                id="navbarDropdownSchool"
                role="button"
                data-bs-toggle="dropdown"
                href="#"
              >
                Skolen
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdownSchool">
                <!-- Students -->
                {#if $hasUserAccessToPath('/students')}
                  <li class="nav-item">
                    <Link to="/students" className="dropdown-item">Elever</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/groups-compare')}
                  <li class="nav-item">
                    <Link to="/groups-compare" className="dropdown-item">Grupper</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/goals')}
                  <li class="nav-item">
                    <Link to="/goals" className="dropdown-item">Mål</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/stats')}
                  <li>
                    <Link to="/stats" className="dropdown-item">Statistikk</Link>
                  </li>
                {/if}
              </ul>
            </li>
          {/if}

          <!-- Superadmin menu -->
          {#if $hasUserAccessToPath('/admin')}
            <li class="nav-item dropdown">
              <!-- svelte-ignore a11y_invalid_attribute -->
              <a
                class={'nav-link dropdown-toggle'}
                class:active={isAdminActive}
                id="navbarDropdownAdmin"
                role="button"
                data-bs-toggle="dropdown"
                href="#"
              >
                Admin
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdownAdmin">
                {#if $hasUserAccessToPath('/admin/schools')}
                  <li>
                    <Link to="/admin/schools" className="dropdown-item">Alle skoler</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/admin/groups')}
                  <li>
                    <Link to="/admin/groups" className="dropdown-item">Grupper adm</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/admin/users')}
                  <li>
                    <Link to="/admin/users" className="dropdown-item">Brukere</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/admin/subjects')}
                  <li>
                    <Link to="/admin/subjects" className="dropdown-item">Fag</Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/admin/status-categories')}
                  <li>
                    <Link to="/admin/status-categories" className="dropdown-item">
                      Statuskategorier
                    </Link>
                  </li>
                {/if}

                {#if $hasUserAccessToPath('/admin/mastery-schemas')}
                  <li>
                    <Link to="/admin/mastery-schemas" className="dropdown-item">
                      Mestringsskjemaer
                    </Link>
                  </li>
                {/if}
                {#if $hasUserAccessToPath('/admin/data-maintenance-tasks')}
                  <li>
                    <Link to="/admin/data-maintenance-tasks" className="dropdown-item">
                      Bakgrunnsjobber
                    </Link>
                  </li>
                {/if}

                {#if $hasUserAccessToPath('/admin/analytics')}
                  <li>
                    <Link to="https://analytics.osloskolen.no/index.php" className="dropdown-item">
                      Analytics
                    </Link>
                  </li>
                {/if}
              </ul>
            </li>
          {/if}

          <!-- User profile menu -->
          {#if $hasUserAccessToPath('/profile')}
            <li class="nav-item dropdown" title="Logget på som {$currentUser.name}">
              <a
                class={'nav-link dropdown-toggle'}
                class:active={isProfileActive}
                id="navbarDropdownProfile"
                role="button"
                data-bs-toggle="dropdown"
                href="#"
              >
                {$currentUser.name.split(' ')[0]}
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdownProfile">
                <li><Link to="/profile" className="dropdown-item">Min side</Link></li>
                <li>
                  <Link to="/" className="dropdown-item" onclick={logout}>Logg ut</Link>
                </li>
              </ul>
            </li>
          {/if}

          <!-- Don't bother the user with this selector if school has only been using mestring this current year -->
          {#if allYearsForCurrentSchool.length > 1}
            <li class="nav-item dropdown" title="Velg skoleår">
              <button
                class={'nav-link dropdown-toggle'}
                class:warning={$preferredSchoolYear !== getCurrentSchoolYear()}
                id="navbarDropdownYearSelector"
                type="button"
                data-bs-toggle="dropdown"
                data-bs-auto-close="outside"
              >
                {$preferredSchoolYear === 'all' ? 'Alle år' : $preferredSchoolYear}
              </button>
              <span
                class="dropdown-menu dropdown-menu-end"
                aria-labelledby="navbarDropdownYearSelector"
              >
                <YearSelector />
              </span>
            </li>
          {/if}
        {/if}

        <!-- Login -->
        {#if !$currentUser}
          <li class="nav-item">
            <Link to="#" className="nav-link" onclick={login}>Logg inn</Link>
          </li>
        {/if}
      </ul>

      <!-- Oslo kommune logo -->
      <a href="https://www.oslo.kommune.no" class="oslo-logo ms-3" target="_blank">
        <img alt="Oslo kommune logo" src={oslologoUrl} />
      </a>
    </div>
  </div>
</nav>

<style>
  h1 {
    font-size: 1.8rem;
    line-height: 1;
    margin: 0;
  }

  .warning {
    background-color: #ffc107;
    border: 2px solid #ff9800;
    border-radius: 3px;
    padding: 5px 0px 4px 0px;
    margin: 0;
  }

  /* Suppress the lingering focus frame after a mouse click,
     but keep it for keyboard users (:focus-visible) for accessibility. */
  nav :global(.nav-link:focus:not(:focus-visible)),
  nav :global(.navbar-brand:focus:not(:focus-visible)) {
    outline: 0;
    box-shadow: none;
  }

  .goal-icon-wrapper {
    position: relative;
    display: inline-flex;
    flex-shrink: 0;
    width: 40px;
    aspect-ratio: 1 / 1;
  }

  .goal-icon-wrapper :global(pkt-icon) {
    display: block;
    position: absolute;
    inset: 0;
  }

  .goal-icon-wrapper .celebration-overlay {
    position: absolute;
    inset: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .oslo-logo img {
    width: 100px;
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

  .navbar-brand-dropdown .dropdown-menu {
    width: max-content;
    min-width: 100%;
  }
</style>
