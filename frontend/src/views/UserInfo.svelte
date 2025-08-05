<script lang="ts">
  import { onMount } from 'svelte'
  import { dataStore, setCurrentSchool } from '../stores/data'
  import { schoolsList, usersGroupsRetrieve } from '../generated/sdk.gen'
  import { urlStringFrom } from '../utils/functions'
  import type { GroupReadable, SchoolReadable } from '../generated/types.gen'
  import { loggedIn } from '../stores/auth'

  let schools = $state<SchoolReadable[]>([])
  let userGroups = $state<GroupReadable[]>([])
  let isLoading = $state(true)
  const isAuthenticated = $derived($loggedIn)

  const currentUser = $derived($dataStore.currentUser)
  const currentSchool = $derived($dataStore.currentSchool)

  const fetchSchools = async () => {
    try {
      const result = await schoolsList()
      schools = (result.data ?? []).filter(x => x.isServiceEnabled)
    } catch (err) {
      console.error('Error fetching schools:', err)
      schools = []
    }
    isLoading = false
  }

  const fetchUserGroups = async () => {
    if (!currentUser?.id) return

    try {
      const result = await usersGroupsRetrieve({
        path: { id: currentUser.id },
        query: { roles: 'student' },
      })
      userGroups = Array.isArray(result.data) ? result.data : []
    } catch (err) {
      console.error('Error fetching user groups:', err)
      userGroups = []
    }
  }

  const selectSchool = (school: SchoolReadable) => {
    setCurrentSchool(school)
  }

  onMount(() => {
    fetchSchools()
    fetchUserGroups()
  })
</script>

<section class="container my-4">
  <h2 class="mb-4">Min side</h2>

  {#if isLoading}
    <div class="text-center my-5">
      <div class="spinner-border" role="status"></div>
    </div>
  {:else if !isAuthenticated}
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
            <strong>Navn:</strong>
            <br />
            {currentUser.name}
          </div>
          <div class="col-md-6">
            <strong>E-post:</strong>
            <br />
            {currentUser.email}
          </div>
        </div>
      </div>
    </div>

    <!-- Usergroup -->
    <div class="card mb-3">
      <div class="card-header d-flex">
        <h5 class="mb-0">
          Mine grupper
          <span class="text-muted">({userGroups.length})</span>
        </h5>
      </div>
      <div class="card-body">
        {#if userGroups.length > 0}
          <div class="list-group list-group-flush">
            {#each userGroups as group}
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
          <span class="text-muted">Ingen skoler tilgjengelig</span>
        {/if}
      </div>
    </div>
  {/if}
</section>
