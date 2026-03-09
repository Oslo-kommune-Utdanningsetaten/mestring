<script lang="ts">
  import { dataStore, setCurrentSchool, currentUser } from '../stores/data'
  import type { GroupType, SchoolType } from '../generated/types.gen'
  import GroupTag from '../components/GroupTag.svelte'

  const schools = $derived<SchoolType[]>($dataStore.currentUser.schools || [])
  const { allGroups, teacherGroups, studentGroups } = $derived($dataStore.currentUser || [])
  const otherGroups = $derived.by(() => {
    if (!allGroups || !teacherGroups || !studentGroups) return []
    return allGroups
      .filter((g: GroupType) => !teacherGroups.map((tg: GroupType) => tg.id).includes(g.id))
      .filter((g: GroupType) => !studentGroups.map((sg: GroupType) => sg.id).includes(g.id))
  })

  const handleSelectSchool = (school: SchoolType) => {
    setCurrentSchool(school)
  }
</script>

<section class="container my-4">
  <h2 class="mb-4">Min side</h2>

  <!-- User Information -->
  <div class="card mb-3">
    <div class="card-header">
      <h3>Brukerinformasjon</h3>
    </div>
    <div class="card-body">
      <div class="row">
        <div class="col-md-4">
          <div class="mb-2">
            <strong>Navn</strong>
            <div class="text-muted">{$currentUser?.name}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="mb-2">
            <strong>E-post</strong>
            <div class="text-muted">{$currentUser?.email}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="mb-2">
            <strong>Intern ID</strong>
            <div class="text-muted">{$currentUser?.id}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- School selection -->
  <div class="card">
    <div class="card-header">
      <h3>Aktiv skole</h3>
    </div>
    <div class="card-body">
      {#if schools.length > 0}
        <div class="row g-2">
          {#each schools as school}
            <div class="col-md-6">
              <button
                class="btn w-100 {$dataStore.currentSchool?.id === school.id
                  ? 'btn-primary'
                  : 'btn-outline-secondary'}"
                onclick={() => handleSelectSchool(school)}
              >
                {school.displayName}
              </button>
            </div>
          {/each}
        </div>
      {:else}
        <span class="text-muted">
          Du er visst ikke tilknyttet noen skoler som bruker denne tjenesten
        </span>
      {/if}
    </div>
  </div>

  <!-- Usergroup -->
  <div class="card mb-3">
    <div class="card-header d-flex">
      <h3 class="mb-0">Grupper jeg har tilgang til ({allGroups?.length})</h3>
    </div>
    <div class="card-body">
      <!-- Teacher groups -->
      <h4 class="mt-1 mb-2">Som lærer</h4>
      {#if teacherGroups?.length > 0}
        <div class="d-flex flex-wrap gap-2">
          {#each teacherGroups as group}
            <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
          {/each}
        </div>
      {:else}
        <span class="text-muted">Ikke medlem av noen grupper som lærer</span>
      {/if}

      <!-- Student groups -->
      <h4 class="mt-4 mb-2">Som elev</h4>
      {#if studentGroups?.length > 0}
        <div class="d-flex flex-wrap gap-2">
          {#each studentGroups as group}
            <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
          {/each}
        </div>
      {:else}
        <span class="text-muted">Ikke medlem av noen grupper som elev</span>
      {/if}

      <!-- Other groups -->
      <h4 class="mt-4 mb-2">Øvirge tilganger</h4>
      {#if otherGroups?.length > 0}
        <div class="d-flex flex-wrap gap-2">
          {#each otherGroups as group}
            <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
          {/each}
        </div>
      {:else}
        <span class="text-muted">Ingen øvrige tilganger</span>
      {/if}
    </div>
  </div>
</section>

<style>
  button {
    border-radius: 0px;
  }
</style>
