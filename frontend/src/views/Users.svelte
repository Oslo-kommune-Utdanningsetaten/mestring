<script lang="ts">
  import { type UserReadable } from '../generated/types.gen'
  import { usersList } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'

  let users = $state<UserReadable[]>([])
  let currentSchool = $derived($dataStore.currentSchool)
  let isLoadingUsers = $state<boolean>(false)

  const fetchUsers = async () => {
    try {
      isLoadingUsers = true
      const result = await usersList({ query: { school: currentSchool.id } })
      users = result.data || []
    } catch (error) {
      console.error('Error fetching users:', error)
      users = []
    } finally {
      isLoadingUsers = false
    }
  }

  $effect(() => {
    if (currentSchool && currentSchool.id) {
      fetchUsers()
    }
  })
</script>

<section class="py-3">
  <h2>Alle brukere på {currentSchool.displayName}</h2>
  <div class="d-flex align-items-center gap-2">
    {#if isLoadingUsers}
      <div class="spinner-border text-primary" role="status"></div>
      <span>Henter brukere...</span>
    {:else}
      <div class="card shadow-sm w-100">
        <!-- Header row -->
        <div class="row fw-bold header p-2">
          <div class="col-4">Navn</div>
          <div class="col-8">Roles</div>
        </div>
        <!-- Data rows -->
        {#each users as user, index}
          <div class="row p-2">
            <div class="col-4">{user.name}</div>
            <div class="col-8">{user.roles}</div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</section>

<style>
</style>
