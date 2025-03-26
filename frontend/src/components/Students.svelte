<script lang="ts">
  import StudentRow from './StudentRow.svelte'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'

  import type {
    Student as StudentType,
    Subject as SubjectType,
    Group as GroupType,
  } from '../types/models'
  import { urlStringFrom } from '../utils/functions'
  const router = useTinyRouter()

  const students = $derived($dataStore.students)
  const subjects = $derived($dataStore.subjects)
  const groups = $derived($dataStore.groups)
  const activeSubjectId = $derived(router.getQueryParam('subjectId'))
  const activeGroupId = $derived(router.getQueryParam('groupId'))
  const activeGroup = $derived(groups.find(g => g.id === activeGroupId))
  const activeSubject = $derived(subjects.find(s => s.id === activeSubjectId))

  // Filter students by group and subject
  const filteredStudents = $derived(
    students
      .filter((student: StudentType) => {
        return activeGroupId ? student.groupId === activeGroupId : true
      })
      .filter((student: StudentType) => {
        return activeSubjectId ? student.subjectIds.includes(activeSubjectId) : true
      })
  )
</script>

<section class="py-3">
  <h2>Elever</h2>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    <div class="dropdown">
      <button
        class="btn btn-outline-secondary dropdown-toggle link-button"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {activeGroup ? activeGroup.name : 'Velg gruppe'}
      </button>
      <ul class="dropdown-menu">
        <li>
          <a
            class="dropdown-item dropdown-link"
            href={urlStringFrom({ groupId: null }, { mode: 'merge' })}
          >
            Alle grupper
          </a>
        </li>
        {#each groups as group}
          <li>
            <a
              class="dropdown-item dropdown-link"
              href={urlStringFrom({ groupId: group.id }, { mode: 'merge' })}
            >
              {group.name}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    <!-- Filter subjects -->
    <div class="dropdown">
      <button
        class="btn btn-outline-secondary dropdown-toggle link-button"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {activeSubject ? activeSubject.name : 'Velg fag'}
      </button>
      <ul class="dropdown-menu">
        <li>
          <a
            class="dropdown-item dropdown-link"
            href={urlStringFrom({ subjectId: null }, { mode: 'merge' })}
          >
            Alle fag
          </a>
        </li>
        {#each subjects as subject}
          <li>
            <a
              class="dropdown-item dropdown-link"
              href={urlStringFrom({ subjectId: subject.id }, { mode: 'merge' })}
            >
              {subject.name}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    <a class="link-button" href={urlStringFrom({}, { mode: 'replace' })}>Nullstill</a>
  </div>
</section>

<section class="py-3">
  {#if filteredStudents.length === 0}
    <div class="alert alert-info">Ingen elever matcher det filteret</div>
  {:else}
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="row fw-bold bg-light border-bottom py-3 mx-0">
        <div class="col-3">Navn</div>
        <div class="col-3">Status</div>
        <div class="col-2">Gruppe</div>
        <div class="col-2">Mål</div>
        <div class="col-2"></div>
      </div>

      <!-- Student rows -->
      {#each filteredStudents as student}
        <StudentRow {student} />
      {/each}
    </div>
  {/if}
</section>

<style>
  .dropdown-link {
    font-size: 1em !important;
  }
  .dropdown-link:hover {
    text-decoration: none;
  }
</style>
