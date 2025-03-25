<script lang="ts">
  import { Router, Route } from 'svelte-tiny-router'
  import Home from './components/Home.svelte'
  import About from './components/About.svelte'
  import Students from './components/Students.svelte'
  import Subjects from './components/Subjects.svelte'
  import Navigation from './components/Navigation.svelte'
  import { loadData } from './stores/data'
  import 'bootstrap/dist/css/bootstrap.min.css'
  import './styles/bootstrap-overrides.css'
  import './styles/app.css'

  // Ensure data is loaded
  loadData()
</script>

<header class="m-0 p-0 vw-100">
  <Navigation />
</header>

<main class="container-md py-4">
  <Router>
    <Route path="/" component={Home} />
    <Route path="/about" component={About} />
    <Route path="/students" component={Students} />
    <Route path="/subjects" component={Subjects} />

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
