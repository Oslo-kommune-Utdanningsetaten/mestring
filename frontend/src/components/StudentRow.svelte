<script lang="ts">
  import {
    type GroupReadable,
    type NestedGroupUserReadable,
    type BasicUserReadable,
  } from '../api/types.gen'
  import { useTinyRouter } from 'svelte-tiny-router'
  const router = useTinyRouter()

  let { student } = $props()
</script>

<div class="student-grid-row">
  <div class="fw-bold">
    {student.name}
  </div>
  <a href={`/students/${student.id}`} class="link-button">Detaljer</a>
</div>

<div class="text-center text-muted py-2">Ingen mål registrert</div>

<style>
</style>
