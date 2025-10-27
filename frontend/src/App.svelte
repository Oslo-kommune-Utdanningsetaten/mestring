<script lang="ts">
  import { Router, Route } from 'svelte-tiny-router'
  import { checkAuth, isLoggingInUser } from './stores/auth'
  import { loadData, currentUser } from './stores/data'
  import { onMount } from 'svelte'
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
  import Navigation from './components/Navigation.svelte'
  import UserInfo from './views/UserInfo.svelte'
  // Admin views
  import Users from './views/admin/Users.svelte'
  import AdminGroups from './views/admin/Groups.svelte'
  import Subjects from './views/admin/Subjects.svelte'
  import MasterySchemas from './views/admin/MasterySchemas.svelte'
  import DataMaintenanceTask from './views/admin/DataMaintenanceTask.svelte'
  import Schools from './views/admin/Schools.svelte'

  // Defer side-effect network calls until after component mount
  onMount(async () => {
    await checkAuth()
    if ($currentUser) {
      loadData()
    }
  })
</script>

<header class="m-0 p-0 vw-100">
  <Navigation />
</header>

<main class="container-md py-3">
  {#if $isLoggingInUser}
    <div class="d-flex align-items-center gap-2 text-secondary small py-2">
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span>Logger inn…</span>
    </div>
  {/if}
  <Router>
    <Route path="/" component={Home} />
    <Route path="/about" component={About} />

    {#if $currentUser}
      <Route path="/students/:studentId" component={Student} />
      <Route path="/groups/:groupId" component={Group} />
      <Route path="/students" component={Students} />
      <Route path="/groups" component={Groups} />
      <Route path="/user-info" component={UserInfo} />
      <Route path="/admin/subjects" component={Subjects} />
      <Route path="/admin/users" component={Users} />
      <Route path="/admin/groups" component={AdminGroups} />
      <Route path="/admin/mastery-schemas" component={MasterySchemas} />
      <Route path="/admin/data-maintenance-tasks" component={DataMaintenanceTask} />
      <Route path="/admin/schools" component={Schools} />
    {/if}

    <!-- Fallback route: no "path" prop means it always matches -->
    <Route>
      <div>
        <h4>Unrecognized path :/</h4>
        <p>The page you're looking for doesn't exist.</p>
      </div>
    </Route>
  </Router>
</main>

<style>
</style>
