<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  const router = useTinyRouter()

  let { student } = $props()
</script>

<div class="student-grid-row">
  <a href={`/students/${student.id}`} class="fw-bold">{student.name}</a>

  <div class="group-grid-columns">
    <span>as</span>
    <span>as</span>
    <span>as</span>
    <span>as</span>
  </div>
</div>

<style>
</style>
