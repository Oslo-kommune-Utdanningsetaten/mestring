<script lang="ts">
  import type { UserReadable, SchoolReadable } from '../../generated/types.gen'
  import { usersList, schoolsList } from '../../generated/sdk.gen'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import { useTinyRouter } from 'svelte-tiny-router'
  import User from '../../components/User.svelte'

  const router = useTinyRouter()
  let users = $state<UserReadable[]>([])
  let schools = $state<SchoolReadable[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let isLoadingUsers = $state<boolean>(false)
  let selectedSchool = $state<SchoolReadable | null>($dataStore.currentSchool)
  let nameFilter = $state<string>('')
  let filteredUsers = $derived(
    nameFilter
      ? users.filter(user => user.name.toLowerCase().includes(nameFilter.toLowerCase()))
      : users
  )

  let headerText = $derived.by(() => {
    let text = selectedSchool ? `Brukere ved: ${selectedSchool.displayName}` : 'Alle brukere'
    text = nameFilter ? `${text} med navn som inneholder "${nameFilter}"` : text
    return text
  })

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const fetchUsers = async () => {
    if (!selectedSchool) return
    try {
      isLoadingUsers = true
      const result = await usersList({ query: { school: selectedSchool.id } })
      users = result.data || []
    } catch (error) {
      console.error('Error fetching users:', error)
      users = []
    } finally {
      isLoadingUsers = false
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    console.log('Selected school ID:', schoolId)
    if (schoolId && schoolId !== '0') {
      router.navigate(urlStringFrom({ school: schoolId }, { path: '/admin/users', mode: 'merge' }))
    } else {
      router.navigate('/admin/users')
    }
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    const selectedSchoolId = router.getQueryParam('school')
    if (selectedSchoolId) {
      selectedSchool = schools.find(school => school.id === selectedSchoolId) || null
    } else {
      selectedSchool = null
    }
    if (selectedSchool && selectedSchool.id) {
      fetchUsers()
    }
  })
</script>

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    {#if isLoadingSchools}
      <div class="m-4">
        <div class="spinner-border text-primary" role="status"></div>
        <span>Henter skoler...</span>
      </div>
    {:else}
      <div class="pkt-inputwrapper">
        <select
          class="pkt-input"
          id="groupSelect"
          onchange={(e: Event) => handleSchoolSelect((e.target as HTMLSelectElement).value)}
        >
          <option value="0" selected={!selectedSchool?.id}>Velg skole</option>
          {#each schools as school}
            <option value={school.id} selected={school.id === selectedSchool?.id}>
              {school.displayName}
            </option>
          {/each}
        </select>
      </div>
      <input
        type="text"
        class="user-filter-input"
        placeholder="Navn på bruker"
        bind:value={nameFilter}
      />
    {/if}
  </div>
</section>

<section class="py-3">
  {#if selectedSchool}
    {#if isLoadingUsers}
      <div class="m-4">
        <div class="spinner-border text-primary" role="status"></div>
        <span>Henter brukere...</span>
      </div>
    {:else if filteredUsers.length === 0}
      <div class="m-4">Ingen brukere funnet</div>
    {:else}
      <div class="card shadow-sm">
        <!-- Header row -->
        <div class="user-grid-row header fw-bold">
          <span>Bruker</span>
          <span>Tilknytninger</span>
          <span></span>
        </div>
        <!-- Data rows -->
        {#each filteredUsers as user}
          <User {user} school={selectedSchool} />
        {/each}
      </div>
    {/if}
  {:else}
    Velg skole for å se brukere
  {/if}
</section>

<style>
  .user-filter-input {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
    margin-left: 10px;
  }
</style>
