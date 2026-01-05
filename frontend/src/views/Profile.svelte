<script lang="ts">
  import { dataStore, setCurrentSchool, currentUser } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import type { GroupType, SchoolType } from '../generated/types.gen'

  let schools = $derived<SchoolType[]>($dataStore.currentUser.schools || [])
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])
  let currentSchool = $derived($dataStore.currentSchool)

  const selectSchool = (school: SchoolType) => {
    setCurrentSchool(school)
  }
</script>

<section class="container my-4">
  <h2 class="mb-4">Min side</h2>

  {#if !$currentUser}
    <div class="alert alert-info">Du må logge inn for å se denne siden.</div>
  {:else}
    <!-- User Information -->
    <div class="card mb-3">
      <div class="card-header">
        <h5>Brukerinformasjon</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <div class="mb-2">
              <strong>Navn</strong>
              <div class="text-muted">{$currentUser?.name}</div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-2">
              <strong>E-post</strong>
              <div class="text-muted">{$currentUser?.email}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usergroup -->
    <div class="card mb-3">
      <div class="card-header d-flex">
        <h5 class="mb-0">
          Mine grupper
          <span class="text-muted">({groups.length})</span>
        </h5>
      </div>
      <div class="card-body">
        {#if groups.length > 0}
          <div class="list-group list-group-flush">
            {#each groups as group}
              <a
                href={urlStringFrom({ groupId: group.id }, { path: '/students', mode: 'replace' })}
                class="list-group-item list-group-item-action"
              >
                {group.displayName}
              </a>
            {/each}
          </div>
        {:else}
          <div class="text-center py-4 text-muted">
            <div>Ingen grupper funnet</div>
          </div>
        {/if}
      </div>
    </div>

    <!-- School selection -->
    <div class="card">
      <div class="card-header">
        <h5>Aktiv skole</h5>
      </div>
      <div class="card-body">
        {#if schools.length > 0}
          <div class="row g-2">
            {#each schools as school}
              <div class="col-md-6">
                <button
                  class="btn w-100 {currentSchool?.id === school.id
                    ? 'btn-primary'
                    : 'btn-outline-secondary'}"
                  onclick={() => selectSchool(school)}
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
  {/if}
</section>
