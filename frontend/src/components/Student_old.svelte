<script lang="ts">
  import type { Student as StudentType, Group as GroupType } from '../types/models'
  import { getGroupById } from '../stores/data'

  // Use $props() instead of export let
  const { student } = $props<{ student: StudentType }>()

  // Get the group for this student
  let group = $state<GroupType | null | undefined>(null)

  // Fetch and set the group when component mounts
  $effect(() => {
    async function loadGroup() {
      group = await getGroupById(student.groupId)
    }
    loadGroup()
  })
</script>

<li class="card mb-3">
  <div class="d-flex card-body align-items-center justify-content-between">
    <div class="student-info">
      <h5 class="card-title mb-0">{student.name}</h5>
      <div class="mt-1">
        <span class="badge bg-secondary me-1">{student.age} år</span>
        <span class="badge bg-info text-dark">{group?.name || student.groupId}</span>
      </div>
    </div>
    <div class="d-flex">
      <button class="btn btn-outline-primary btn-sm me-2">Mål</button>
      <button
        class="btn btn-outline-secondary btn-sm"
        on:click={() => {
          console.log('unimplemented')
        }}
        title="observations"
      >
        Observasjoner
      </button>
    </div>
  </div>
</li>
