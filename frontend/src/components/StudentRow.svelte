<script lang="ts">
  import StudentStatus from './StudentStatus.svelte'

  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'
  import type {
    Student as StudentType,
    Subject as SubjectType,
    Group as GroupType,
  } from '../types/models'
  import { urlStringFrom } from '../utils/functions'
  const router = useTinyRouter()

  const { student } = $props<{ student: StudentType }>()

  const subjects = $derived($dataStore.subjects)
  const groups = $derived($dataStore.groups)

  let isOpen = $state(false)
</script>

<div class="row py-2 mx-0 align-items-center {isOpen ? 'border-bottom-dotted' : 'border-bottom'} ">
  <div class="col-4 fw-bold">
    <a onclick={() => (isOpen = !isOpen)}>
      {student.name}
    </a>
  </div>
  <div class="col-2 text-center"><StudentStatus {student} /></div>
  <div class="col-2 text-center">
    {groups.find(g => g.id === student.groupId)?.name || ''}
  </div>
  <div class="col-2 text-center">
    {$dataStore.goals.filter(g => g.studentId === student.id).length}
  </div>
  <div class="col-2">
    <div class="d-flex gap-2 justify-content-center">
      <a href={`/students/${student.id}`} class="link-button">Profil</a>
      <a href={`/goals/?studentId=${student.id}`} class="link-button">Mål</a>
    </div>
  </div>
</div>
{#if isOpen}
  <div class="row border-bottom py-2 mx-0 align-items-center">
    <div class="col-12">asdf</div>
  </div>
{/if}

<style>
  .border-bottom-dotted {
    border-bottom: 1px dashed var(--bs-primary-rgb);
  }
</style>
