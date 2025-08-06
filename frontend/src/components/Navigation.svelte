<script lang="ts">
  import Link from './Link.svelte'
  import oslologoUrl from '@oslokommune/punkt-assets/dist/logos/oslologo.svg?url'

  import { currentPath } from '../stores/navigation'
  import { dataStore } from '../stores/data'
  import { apiHealth } from '../stores/apiHealth'
  import { onMount } from 'svelte'
  import { currentUser, checkAuth, login, logout } from '../stores/auth'

  let isHomeActive = $derived($currentPath === '/')
  let isAboutActive = $derived($currentPath === '/about')
  let isStudentsActive = $derived($currentPath.startsWith('/students'))
  let isSchoolsActive = $derived($currentPath.startsWith('/schools'))

  $effect(() => {
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

  onMount(checkAuth)
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
        {#if $currentUser}
          <li class="nav-item">
            <Link to="/" className={`nav-link ${isHomeActive ? 'active' : ''}`}>Hjem</Link>
          </li>
          <li class="nav-item">
            <Link to="/students" className={`nav-link ${isStudentsActive ? 'active' : ''}`}>
              Elever
            </Link>
          </li>
        {/if}
        <li class="nav-item">
          <Link to="/about" className={`nav-link ${isAboutActive ? 'active' : ''}`}>
            Om&nbsp;tjenesten
          </Link>
        </li>
        {#if $currentUser}
          <li class="nav-item dropdown">
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

        {#if $currentUser}
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
                <a class="dropdown-item" href="/schools">Skoler</a>
              </li>
              <li><a class="dropdown-item" href="/mastery-schemas">Mastery Schemas</a></li>
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

  .selected-school {
    background-color: #f8f9fa;
    color: #000;
    font-weight: bold;
  }
</style>
