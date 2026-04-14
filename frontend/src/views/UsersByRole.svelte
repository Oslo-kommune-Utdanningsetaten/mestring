<script lang="ts">
  import type { UserType } from '../generated/types.gen'
  import { usersList } from '../generated/sdk.gen'
  import Link from '../components/Link.svelte'
  import { dataStore } from '../stores/data'
  import { useTinyRouter } from 'svelte-tiny-router'

  const router = useTinyRouter()

  const roleName = $derived(router.getQueryParam('role'))
  const teacherType = $derived(router.getQueryParam('teacherType'))
  const currentSchool = $derived($dataStore.currentSchool)
  const rolesLookup = {
    teacher: 'lærer',
    student: 'elev',
    inspector: 'inspektør',
    admin: 'administrator',
    teaching: 'undervisnings',
    basis: 'basis',
  }

  const heading = $derived.by(() => {
    let result = 'Brukere med rolle: '
    if (teacherType) {
      result += `${rolesLookup[teacherType as keyof typeof rolesLookup] || teacherType}`
    }
    if (roleName) {
      result += `${rolesLookup[roleName as keyof typeof rolesLookup] || roleName}`
    }
    return result
  })

  let users = $state<UserType[]>([])

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

<h3 class="my-3">{heading}</h3>
<ul>
  {#each users as user}
    <li>
      <Link to={`/admin/users/${user.id}`}>{user.name}</Link>
    </li>
  {/each}
</ul>

<style>
</style>
