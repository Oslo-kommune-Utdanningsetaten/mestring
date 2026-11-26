<script lang="ts">
  import type { UserType } from '../generated/types.gen'
  import { usersList } from '../generated/sdk.gen'
  import Link from '../components/Link.svelte'
  import { dataStore } from '../stores/data'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { USER_ROLES } from '../utils/constants'

  import RoleDescription from '../components/RoleDescription.svelte'

  const router = useTinyRouter()

  const roleName = $derived(router.getQueryParam('role'))
  const teacherType = $derived(router.getQueryParam('teacherType'))
  const currentSchool = $derived($dataStore.currentSchool)

  let users = $state<UserType[]>([])

  const acceptedToRoles = [
    USER_ROLES.ADMIN,
    USER_ROLES.TEACHER,
    USER_ROLES.INSPECTOR,
    USER_ROLES.SUPERADMIN,
  ]

  const fetchUsers = async () => {
    if (!roleName || !currentSchool) return null
    const query: any = { roles: roleName, school: currentSchool.id }
    if (teacherType) {
      query['teacher'] = teacherType
    }
    const result = await usersList({ query })
    users = result.data || []
  }

  $effect(() => {
    fetchUsers()
  })
</script>

{#if roleName && acceptedToRoles.includes(roleName as USER_ROLES)}
  <h3 class="my-3">Brukere med rolle: {roleName}{teacherType ? `, ${teacherType}` : ''}</h3>
  {#if roleName === USER_ROLES.TEACHER}
    <div>
      <RoleDescription roleNames={[roleName]} options={{ teacherType }} />
    </div>
  {:else}
    <div>
      <RoleDescription roleNames={[roleName]} />
    </div>
  {/if}
  <ul class="mt-3">
    {#each users as user}
      <li>
        <Link to={`/users/${user.id}`}>{user.name}</Link>
      </li>
    {/each}
  </ul>
{:else}
  Hmm.
{/if}

<style>
</style>
