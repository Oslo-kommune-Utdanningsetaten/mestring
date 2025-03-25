<script lang="ts">
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'
  import { useTinyRouter } from 'svelte-tiny-router'

  const router = useTinyRouter()
  console.log(window.location.pathname)

  function getCurrentSubject() {
    const path = window.location.pathname
    const subjectId = path.split('/').pop()
    return subjectId || router.getQueryParam('subjectId')
  }

  // Convert to nullable type for reactive filters
  $: activeSubjectId = getCurrentSubject()

  // Reactive declarations for data
  $: subjects = $dataStore.subjects || []
  $: goals = $dataStore.goals || []
  $: students = $dataStore.students || []

  // Get the active subject for display
  $: activeSubject = activeSubjectId ? subjects.find(s => s.id === activeSubjectId) : null

  // Get goals for the active subject
  $: subjectGoals = activeSubjectId ? goals.filter(goal => goal.subjectId === activeSubjectId) : []

  // Get students that have goals in the current subject
  $: studentsInSubject = activeSubjectId
    ? [...new Set(subjectGoals.map(goal => goal.studentId))]
        .map(studentId => students.find(s => s.id === studentId))
        .filter(student => student !== undefined)
    : []
</script>

<section class="py-4">
  <h1 class="mb-4">
    {#if activeSubject}
      {activeSubject.name}
    {:else}
      Alle fag
    {/if}
  </h1>

  {#if !activeSubject}
    <!-- Show all subjects in a table-like grid layout using Bootstrap classes -->
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="row fw-bold bg-light border-bottom py-3 mx-0">
        <div class="col-5">Fagnavn</div>
        <div class="col-2 text-center">Mål</div>
        <div class="col-2 text-center">Elever</div>
        <div class="col-3 text-center">🔎</div>
      </div>

      <!-- Subject rows -->
      {#each subjects as subject (subject.id)}
        <div class="row border-bottom py-3 mx-0 align-items-center">
          <div class="col-5 fw-bold">
            <Link to={`/goals/?subjectId=${subject.id}`}>
              {subject.name}
            </Link>
          </div>
          <div class="col-2 text-center">
            {goals.filter(goal => goal.subjectId === subject.id).length}
          </div>
          <div class="col-2 text-center">
            {[
              ...new Set(
                goals.filter(goal => goal.subjectId === subject.id).map(goal => goal.studentId)
              ),
            ].length}
          </div>
          <div class="col-3 text-center">
            <div class="d-flex gap-2 justify-content-center">
              <Link to={`/goals/?subjectId=${subject.id}`}>Mål</Link>
              <Link to={`/students/?subjectId=${subject.id}`}>Elever</Link>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- Show subject details when one is selected -->
    <div class="mb-4">
      <Link to="/subjects" className="btn btn-outline-secondary">
        <i class="bi bi-arrow-left"></i>
        Tilbake til alle fagområder
      </Link>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="mb-4">
          <h2 class="h4">{activeSubject.name}</h2>
          <p class="mb-1">{subjectGoals.length} mål totalt</p>
          <p>{studentsInSubject.length} elever med mål i dette faget</p>
        </div>

        <div>
          <h3 class="h5 mb-3">Elever med mål i {activeSubject.name}:</h3>
          <ul class="list-group">
            {#each studentsInSubject as student}
              <li class="d-flex list-group-item align-items-center justify-content-between">
                <Link to={`/students/${student.id}`} className="text-decoration-none">
                  {student.name}
                </Link>
                <span class="badge bg-primary rounded-pill">
                  {goals.filter(
                    goal => goal.studentId === student.id && goal.subjectId === activeSubjectId
                  ).length} mål
                </span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    </div>
  {/if}
</section>
