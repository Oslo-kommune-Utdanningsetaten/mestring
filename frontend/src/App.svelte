<script lang="ts">
  import { Router, Route } from 'svelte-tiny-router'
  import { onMount } from 'svelte'
  import { checkAuth, isLoggingInUser, login } from './stores/auth'
  import { loadData, currentUser, dataStore } from './stores/data'
  import { apiHealth } from './stores/apiHealth'
  import { addAlert } from './stores/alerts'

  import 'bootstrap/dist/css/bootstrap.min.css'
  import './styles/bootstrap-overrides.css'
  import 'bootstrap/dist/js/bootstrap.min.js'
  import './styles/app.css'
  // Views
  import Home from './views/Home.svelte'
  import About from './views/About.svelte'
  import Student from './views/Student.svelte'
  import Group from './views/Group.svelte'
  import Groups from './views/Groups.svelte'
  import Students from './views/Students.svelte'
  import Status from './views/Status.svelte'
  import Profile from './views/Profile.svelte'
  import NotFound from './views/NotFound.svelte'
  // Admin views
  import Users from './views/admin/Users.svelte'
  import AdminGroups from './views/admin/Groups.svelte'
  import Subjects from './views/admin/Subjects.svelte'
  import MasterySchemas from './views/admin/MasterySchemas.svelte'
  import DataMaintenanceTask from './views/admin/DataMaintenanceTask.svelte'
  import Schools from './views/admin/Schools.svelte'
  // Conponents
  import Navigation from './components/Navigation.svelte'
  import ButtonMini from './components/ButtonMini.svelte'
  import AlertBar from './components/AlertBar.svelte'

  const API_CHECK_INTERVAL = 60 * 1000 // every 60 seconds

  // All routes in the app
  const routes = [
    { path: '/', component: Home },
    { path: '/about', component: About },
    { path: '/groups', component: Groups },
    { path: '/groups/:groupId', component: Group },
    { path: '/profile', component: Profile },
    { path: '/students', component: Students },
    { path: '/statuses/:statusId', component: Status },
    { path: '/students/:studentId', component: Student },
    { path: '/admin/users', component: Users },
    { path: '/admin/groups', component: AdminGroups },
    { path: '/admin/subjects', component: Subjects },
    { path: '/admin/mastery-schemas', component: MasterySchemas },
    { path: '/admin/data-maintenance-tasks', component: DataMaintenanceTask },
    { path: '/admin/schools', component: Schools },
  ]

  onMount(() => {
    apiHealth.checkHealth()

    checkAuth().then(() => {
      if ($currentUser) {
        loadData()
      }
    })
    // Periodically check API health
    const interval = setInterval(() => {
      apiHealth.checkHealth()
      if (!$apiHealth.isOk) {
        addAlert({
          type: 'danger',
          message: `Connection issues. API: ${$apiHealth.api} | DB: ${$apiHealth.db} 😬`,
          isPersistent: true,
        })
      }
    }, API_CHECK_INTERVAL)

    return () => {
      clearInterval(interval)
    }
  })
</script>

<header class="m-0 p-0 vw-100">
  <Navigation />
  <AlertBar />
</header>

<main class="container-md py-3">
  {#if $isLoggingInUser}
    <div class="d-flex align-items-center gap-2 text-secondary small py-2">
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span>Logger inn...</span>
    </div>
  {:else}
    <Router>
      {#each routes as route}
        {#if $dataStore.hasUserAccessToPath(route.path)}
          <Route path={route.path} component={route.component} />
        {/if}
      {/each}
      <!-- Fallback route: no "path" prop means it always matches -->
      <Route>
        <NotFound />
      </Route>
    </Router>
  {/if}
</main>

<style>
</style>
