<script lang="ts">
  import { Router, Route } from 'svelte-tiny-router'
  import Home from './views/Home.svelte'
  import About from './views/About.svelte'
  import Student from './views/Student.svelte'
  import Group from './views/Group.svelte'
  import Schools from './views/Schools.svelte'
  import Students from './views/Students.svelte'
  import Subjects from './views/Subjects.svelte'
  import Navigation from './components/Navigation.svelte'
  import MasterySchemas from './views/MasterySchemas.svelte'
  import { loadData } from './stores/data'
  import 'bootstrap/dist/css/bootstrap.min.css'
  import 'bootstrap/dist/js/bootstrap.min.js'
  import './styles/bootstrap-overrides.css'
  import './styles/app.css'

  loadData()
</script>

<header class="m-0 p-0 vw-100">
  <Navigation />
</header>

<main class="container-md py-4">
  <Router>
    <Route path="/" component={Home} />
    <Route path="/about" component={About} />
    <Route path="/students/:studentId" component={Student} />
    <Route path="/groups/:groupId" component={Group} />
    <Route path="/schools" component={Schools} />
    <Route path="/students" component={Students} />
    <Route path="/subjects" component={Subjects} />
    <Route path="/mastery-schemas" component={MasterySchemas} />

    <!-- Fallback route: no "path" prop means it always matches -->
    <Route>
      <div class="alert alert-danger">
        <h4>Page not found :/</h4>
        <p>The page you're looking for doesn't exist.</p>
      </div>
    </Route>
  </Router>
</main>

<style>
</style>
