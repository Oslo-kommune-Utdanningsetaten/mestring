<script lang="ts">
  import type { UserType, SchoolType, UserDecorated } from '../../generated/types.gen'
  import { usersList, schoolsList } from '../../generated/sdk.gen'
  import { urlStringFrom, fetchUserData } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { UserRoles } from '../../utils/constants'
  import User from '../../components/User.svelte'

  const router = useTinyRouter()
  let users = $state<UserType[]>([])
  let schools = $state<SchoolType[]>([])
  let isLoadingSchools = $state<boolean>(false)
  let isLoadingUsers = $state<boolean>(false)
  let selectedSchool = $state<SchoolType | null>($dataStore.currentSchool)
  let selectedRoles = $state<string[]>([
    UserRoles.TEACHER,
    UserRoles.ADMIN,
    UserRoles.INSPECTOR,
    UserRoles.STAFF,
  ])
  let deletedSelection = $state<'include' | 'only' | 'exclude'>('include')

  let nameFilter = $state<string>('')
  let filteredUsers = $derived(
    nameFilter
      ? users.filter(
          user =>
            user.name.toLowerCase().includes(nameFilter.toLowerCase()) ||
            user.feideId.toLowerCase().includes(nameFilter.toLowerCase())
        )
      : users
  )
  let decoratedUsersById = $state<Record<string, UserDecorated>>({})

  // Options for filtering by role
  const roleOptions = [
    { value: 'all', label: 'Alle' },
    { value: UserRoles.TEACHER, label: 'Lærere' },
    { value: UserRoles.STUDENT, label: 'Elever' },
    { value: UserRoles.ADMIN, label: 'Admins' },
    { value: UserRoles.INSPECTOR, label: 'Inspektører' },
    { value: UserRoles.STAFF, label: 'Skoleansatte uten rolle' },
  ] as const

  // Options for filtering by deleted
  const deletedOptions = [
    { value: 'include', label: 'All' },
    { value: 'only', label: 'Deleted' },
    { value: 'exclude', label: 'Non-deleted' },
  ] as const

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
    const roles = selectedRoles.includes('all') ? [] : selectedRoles
    try {
      isLoadingUsers = true
      const result = await usersList({
        query: { school: selectedSchool.id, deleted: deletedSelection, roles: roles.join(',') },
      })
      users = result.data || []
      users.forEach(user => {
        if (!decoratedUsersById[user.id]) {
          fetchUserAffiliations(user)
        }
      })
    } catch (error) {
      console.error('Error fetching users:', error)
      users = []
    } finally {
      isLoadingUsers = false
    }
  }

  const fetchUserAffiliations = async (user: UserType) => {
    if (!selectedSchool) return
    try {
      const { teacherGroups, studentGroups, userSchools } = await fetchUserData(
        user.id,
        selectedSchool.id
      )
      const decoratedUser = { ...user, teacherGroups, studentGroups, userSchools }
      decoratedUsersById = { ...decoratedUsersById, [user.id]: decoratedUser }
    } catch (error) {
      console.error('Error fetching user data:', user.id, error)
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(urlStringFrom({ school: schoolId }, { path: '/admin/users', mode: 'merge' }))
    } else {
      router.navigate('/admin/users')
    }
  }

  const handleRoleSelect = (role: string): void => {
    let newRoles = []
    if (selectedRoles.includes(role)) {
      newRoles = selectedRoles.filter(r => r !== role)
    } else {
      newRoles = [...selectedRoles, role]
    }
    if (newRoles.includes('all')) {
      // 'all' is present, if it was added, remove all other options, if it was removed, keep all other options
      newRoles = role === 'all' ? ['all'] : newRoles.filter(r => r !== 'all')
    }
    if (newRoles.length === 0) {
      // If no roles are selected, default to 'all'
      newRoles = ['all']
    }
    selectedRoles = newRoles
  }

  const getResultDescription = (): string => {
    const count = filteredUsers.length
    let result = `${count} brukere`
    if (count === 0) result = 'Ingen brukere'
    if (count === 1) result = '1 bruker'
    return result
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    if (!router.getQueryParam('school') && $dataStore.currentSchool) {
      handleSchoolSelect($dataStore.currentSchool.id)
    }
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
  {#if isLoadingSchools}
    <div class="m-4">
      <div class="spinner-border text-primary" role="status"></div>
      <span>Henter skoler...</span>
    </div>
  {:else}
    <div class="filters-container">
      <div class="filter-item">
        <label for="schoolSelect" class="mb-1 visually-hidden">Filtrer på skole:</label>
        <select
          class="pkt-input"
          id="schoolSelect"
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
      <div class="filter-item">
        <label for="userFilterInput" class="mb-1 visually-hidden">Filtrer på navn:</label>
        <input
          type="text"
          id="userFilterInput"
          class="user-filter-input"
          placeholder="Navn på bruker"
          bind:value={nameFilter}
        />
      </div>
    </div>
    <!-- Radio buttons for role status -->
    <div class="d-flex flex-wrap gap-3 mt-3">
      <fieldset class="border p-3 rounded">
        <legend class="w-auto fs-6">Brukere med rolle</legend>
        {#each roleOptions as option (option.value)}
          <label class="my-2 ms-1 d-block">
            <input
              type="checkbox"
              name="roleOptions"
              value={option.value}
              onclick={() => handleRoleSelect(option.value)}
              checked={selectedRoles.includes(option.value)}
              disabled={option.value === 'all' && selectedRoles.length === 1}
            />
            <span class="ms-2">{option.label}</span>
          </label>
        {/each}
      </fieldset>

      <!-- Radio buttons for deleted status -->
      <fieldset class="border p-3 rounded">
        <legend class="w-auto fs-6">Deleted?</legend>
        {#each deletedOptions as option}
          <label class="my-2 ms-1 d-block">
            <input
              type="radio"
              name="deletedOptions"
              value={option.value}
              bind:group={deletedSelection}
            />
            <span class="ms-2">{option.label}</span>
          </label>
        {/each}
      </fieldset>
    </div>
  {/if}
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
      <div class="my-4">Fant {getResultDescription()}</div>
      <div class="card shadow-sm">
        <!-- Header row -->
        <div class="user-grid-row header fw-bold">
          <span>User</span>
          <span>Cr.</span>
          <span>Mem.</span>
          <span>Affiliations</span>
          <span>Role</span>
        </div>
        <!-- Data rows -->
        {#each filteredUsers as user (user.id)}
          <User {user} decoratedUser={decoratedUsersById[user.id]} school={selectedSchool} />
        {/each}
      </div>
    {/if}
  {:else}
    Velg skole for å se brukere
  {/if}
</section>

<style>
  .filters-container {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    flex: 1 1 20rem;
    min-width: 3rem;
    max-width: 25rem;
  }

  .user-filter-input {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
  }
</style>
