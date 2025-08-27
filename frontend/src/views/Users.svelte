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
      <ul class="list-group w-100">
        {#each users as user}
          <li class="list-group-item d-flex justify-content-between align-items-center">
            {user.name}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</section>

<style>
</style>
