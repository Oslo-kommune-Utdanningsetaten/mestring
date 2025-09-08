<script lang="ts">
  import { Router, Route } from 'svelte-tiny-router'
  import Home from './views/Home.svelte'
  import About from './views/About.svelte'
  import Student from './views/Student.svelte'
  import Group from './views/Group.svelte'
  import Schools from './views/Schools.svelte'
  import Students from './views/Students.svelte'
  import Users from './views/Users.svelte'
  import Subjects from './views/Subjects.svelte'
  import Navigation from './components/Navigation.svelte'
  import MasterySchemas from './views/MasterySchemas.svelte'
  import UserInfo from './views/UserInfo.svelte'
  import { checkAuth, isLoggingInUser } from './stores/auth'
  import { loadData, dataStore } from './stores/data'
  import { onMount } from 'svelte'
  import 'bootstrap/dist/css/bootstrap.min.css'
  import './styles/bootstrap-overrides.css'
  import 'bootstrap/dist/js/bootstrap.min.js'
  import './styles/app.css'

  // Defer sideeffect network calls until after component mount
  onMount(async () => {
    await checkAuth()
    if ($dataStore.currentUser) {
      loadData()
    }
  })
</script>

<header class="m-0 p-0 vw-100">
  <Navigation />
</header>

<main class="container-md py-4">
  {#if $isLoggingInUser}
    <div class="d-flex align-items-center gap-2 text-secondary small py-2">
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span>Logger inn…</span>
    </div>
  {/if}
  <Router>
    <Route path="/" component={Home} />
    <Route path="/about" component={About} />

    {#if $dataStore.currentUser}
      <Route path="/students/:studentId" component={Student} />
      <Route path="/groups/:groupId" component={Group} />
      <Route path="/students" component={Students} />
      <Route path="/user-info" component={UserInfo} />
      <Route path="/subjects" component={Subjects} />
      <Route path="/users" component={Users} />
      <Route path="/mastery-schemas" component={MasterySchemas} />
      <Route path="/schools" component={Schools} />
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
