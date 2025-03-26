<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore, getSubjectById } from '../stores/data'
  import Student from './Student.svelte'
  import Link from './Link.svelte'

  import type {
    Student as StudentType,
    Subject as SubjectType,
    Group as GroupType,
  } from '../types/models'
  import { urlStringFrom } from '../utils/functions'
  const router = useTinyRouter()

  // Get parameters from routes if they exist
  export let subjectId: string | undefined = undefined
  export let groupId: string | undefined = undefined

  $: students = $dataStore.students
  $: subjects = $dataStore.subjects
  $: groups = $dataStore.groups || []
  $: activeSubjectId = subjectId || router.getQueryParam('subjectId')
  $: activeGroupId = groupId || router.getQueryParam('groupId')
  $: activeGroup = groups.find(g => g.id === activeGroupId)
  $: activeSubject = subjects.find(s => s.id === activeSubjectId)

  // Filter students by group and subject
  $: filteredStudents = students
    .filter((student: StudentType) => {
      return activeGroupId ? student.groupId === activeGroupId : true
    })
    .filter((student: StudentType) => {
      return activeSubjectId ? student.subjectIds.includes(activeSubjectId) : true
    })
</script>

<section class="py-4">
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

<section class="py-4">
  {#if filteredStudents.length === 0}
    <div class="alert alert-info">Ingen elever funnet</div>
  {:else}
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="row fw-bold bg-light border-bottom py-3 mx-0">
        <div class="col-4">Navn</div>
        <div class="col-3">Gruppe</div>
        <div class="col-2 text-center">Mål</div>
        <div class="col-3 text-center">🔎</div>
      </div>

      <!-- Student rows -->
      {#each filteredStudents as student (student.id)}
        <div class="row border-bottom py-2 mx-0 align-items-center">
          <div class="col-4 fw-bold">
            <Link to={''}>
              {student.name}
            </Link>
          </div>
          <div class="col-3">
            {groups.find(g => g.id === student.groupId)?.name || ''}
          </div>
          <div class="col-2 text-center">
            {$dataStore.goals.filter(g => g.studentId === student.id).length}
          </div>
          <div class="col-3">
            <div class="d-flex gap-2 justify-content-center">
              <a href={`/students/${student.id}`} class="link-button">Profil</a>
              <a href={`/goals/?studentId=${student.id}`} class="link-button">Mål</a>
            </div>
          </div>
        </div>
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
