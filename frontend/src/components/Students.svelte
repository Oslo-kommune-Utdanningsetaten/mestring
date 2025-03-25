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

  // Convert to nullable types for reactive filters
  $: subject = subjectId || router.getQueryParam('subjectId')
  $: group = groupId || router.getQueryParam('groupId')

  // Reactive declarations for data
  $: students = $dataStore.students
  $: subjects = $dataStore.subjects
  $: groups = $dataStore.groups || []

  // Get the subject name for display if a subject is selected
  $: currentSubject = subject ? subjects.find((s: SubjectType) => s.id === subject) : null

  // Get the group name for display if a group is selected
  $: currentGroup = group ? groups.find((g: GroupType) => g.id === group) : null

  // Filter students by both group and subject if provided
  $: filteredStudents = students.filter((student: StudentType) => {
    // Filter by group if a group is specified
    if (group && student.groupId !== group) return false
    return true
  })
</script>

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
        <div class="row border-bottom py-3 mx-0 align-items-center">
          <div class="col-4 fw-bold">
            <Link to={urlStringFrom({ studentId: student.id })}>
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
              <a href={`/students/${student.id}`} class="btn btn-primary btn-sm">Profil</a>
              <a href={`/goals/?studentId=${student.id}`} class="btn btn-outline-secondary btn-sm">
                Mål
              </a>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>
