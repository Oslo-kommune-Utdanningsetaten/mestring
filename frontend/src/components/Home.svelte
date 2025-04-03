<script lang="ts">
  import Link from './Link.svelte'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  const currentUser = $derived($dataStore.currentUser)
  const groups = $derived(
    $dataStore.groups.filter(
      g => currentUser?.teacherId && g.teacherIds?.includes(currentUser.teacherId)
    )
  )
  const students = $derived($dataStore.students)
  const teachers = $derived($dataStore.teachers)
</script>

<section class="py-3">
  <h2 class="mb-4">Mine grupper</h2>
  <p class="d-flex align-items-center gap-2">
    Hei, {currentUser?.name}! Dette er gruppene du har tilgang til.
  </p>

  <section class="py-3">
    {#if groups.length === 0}
      <div class="alert alert-info">Du har visst ikke tilgang til noen grupper</div>
    {:else}
      <div class="card shadow-sm">
        <!-- Header row -->
        <div class="row fw-bold bg-light border-bottom py-3 mx-0">
          <div class="col-2">Gruppe</div>
          <div class="col-2">Elever</div>
          <div class="col-8">Lærere</div>
        </div>

        <!-- Student rows -->
        {#each groups as group}
          <div class="row py-2 align-items-center mx-0 border">
            <div class="col-2 fw-bold">
              <a
                href={urlStringFrom(
                  group.type === 'basis'
                    ? { basisGroupId: group.id }
                    : { teachingGroupId: group.id },
                  {
                    path: '/students',
                    mode: 'replace',
                  }
                )}
              >
                {group.name}
              </a>
            </div>
            <div class="col-2">
              {students.filter(s => s.groupIds.includes(group.id)).length}
            </div>
            <div class="col-8">
              {teachers
                .filter(t => group.teacherIds?.includes(t.id))
                .map(t => t.name)
                .join(', ')}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
</section>

<style>
</style>
