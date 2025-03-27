<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { Student as StudentType, Group as GroupType } from '../types/models'

  const { studentId } = $props<{ studentId: string }>()
  const students = $derived($dataStore.students)
  const student: StudentType | undefined = $derived(students.find(s => s.id === studentId))
</script>

<section class="py-3">
  {#if student}
    <h2>{student.name}</h2>
    <div class="student-info"></div>
  {:else}
    <div class="alert alert-danger">Fant ikke eleven</div>
  {/if}
</section>
