<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type {
    NestedUserGroupType,
    NestedUserSchoolType,
    SchoolType,
    UserType,
  } from '../generated/types.gen'
  import type { UserDecorated } from '../types/models.d.ts'
  import { userSchoolsDestroy, userSchoolsCreate } from '../generated/sdk.gen'
  import { SCHOOL_ADMIN_ROLE, SCHOOL_INSPECTOR_ROLE, NONE_FIELD_VALUE } from '../utils/constants'
  import { dataStore } from '../stores/data'
  import GroupTag from './GroupTag.svelte'
  import { formatDate } from '../utils/functions'
  import SinceSchoolStart from './SinceSchoolStart.svelte'

  const { user, decoratedUser, school, onUserUpdate } = $props<{
    user: UserType
    decoratedUser: UserDecorated
    school: SchoolType
    onUserUpdate: (userId: string) => Promise<void>
  }>()

  let isSchoolInspector = $derived(
    !!decoratedUser.userSchools.find(
      (us: NestedUserSchoolType) =>
        us.role.name === SCHOOL_INSPECTOR_ROLE && us.school.id === school.id
    )
  )
  let isSchoolAdmin = $derived(
    !!decoratedUser.userSchools.find(
      (us: NestedUserSchoolType) => us.role.name === SCHOOL_ADMIN_ROLE && us.school.id === school.id
    )
  )
  const relevantSchoolRoles = [SCHOOL_INSPECTOR_ROLE, SCHOOL_ADMIN_ROLE]
  let selectedSchoolRole = $derived(
    isSchoolAdmin ? SCHOOL_ADMIN_ROLE : isSchoolInspector ? SCHOOL_INSPECTOR_ROLE : NONE_FIELD_VALUE
  )

  let newestMembership: NestedUserGroupType | null = $derived(
    [...decoratedUser.userGroups].sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )[0]
  )

  const handleRoleChange = async (roleName: string) => {
    if (!decoratedUser.id || !school.id || !roleName) {
      console.error('Missing information', decoratedUser, school, roleName)
      return
    }

    const confirmed = confirm(
      `Er du sikker på at du vil endre ${decoratedUser.name} sin rolle til ${roleName}?`
    )

    if (!confirmed) return

    try {
      // Remove all existing roles
      await Promise.all(
        decoratedUser.userSchools
          .filter((userSchool: NestedUserSchoolType) =>
            relevantSchoolRoles.includes(userSchool.role.name)
          )
          .map(async (userSchool: NestedUserSchoolType) => {
            return await userSchoolsDestroy({
              path: {
                id: userSchool.id,
              },
            })
          })
      )
      // Add new role
      const roleToAssign = $dataStore.roles?.find(role => role.name === roleName)
      if (roleToAssign) {
        await userSchoolsCreate({
          body: { userId: decoratedUser.id, schoolId: school.id, roleId: roleToAssign.id },
        })
      }
    } catch (error) {
      console.error('Error while changing role:', error)
    } finally {
      onUserUpdate(decoratedUser.id)
    }
  }
</script>

<div class="user-grid-row">
  <div>
    <div class="fw-semibold">{user.name}</div>
    <div class="text-muted small">{user.email || 'Ingen e-post'}</div>
    <div class="text-muted small">{user.id}</div>
  </div>
  <div>
    <div class="text-muted small">{formatDate(user.createdAt)}</div>
    <SinceSchoolStart dateAsString={user.createdAt} />
  </div>
  {#if decoratedUser}
    <div>
      <div class="text-muted small">{formatDate(newestMembership?.createdAt)}</div>
      <SinceSchoolStart dateAsString={newestMembership?.createdAt} />
    </div>
    <div class="small">
      <div class="group-type-heading">Lærer</div>
      <ul class="group-list">
        {#each decoratedUser.teacherGroups as group (group.id)}
          <li>
            <GroupTag
              {group}
              isGroupNameEnabled={true}
              href={group.isEnabled ? `/groups/${group.id}/` : undefined}
            />
          </li>
        {/each}
      </ul>

      <div class="group-type-heading">Elev</div>
      <ul class="group-list">
        {#each decoratedUser.studentGroups as group (group.id)}
          <li>
            <GroupTag
              {group}
              isGroupNameEnabled={true}
              href={group.isEnabled ? `/groups/${group.id}/` : undefined}
            />
          </li>
        {/each}
      </ul>
    </div>

    <div>
      <div class="mb-1">
        <strong>
          {decoratedUser.userSchools
            .map((userSchool: NestedUserSchoolType) => userSchool.role.name)
            .join(', ') || 'Ingen'}
        </strong>
      </div>
      <pkt-select
        name="userSchoolRole"
        value={selectedSchoolRole}
        onchange={(e: Event) => {
          const target = e.target as HTMLSelectElement | null
          const roleName = target?.value || NONE_FIELD_VALUE
          handleRoleChange(roleName)
        }}
      >
        <option value={NONE_FIELD_VALUE}>none</option>
        {#each relevantSchoolRoles as option}
          <option value={option}>
            {option}
          </option>
        {/each}
      </pkt-select>
    </div>
  {:else}
    <div class="spinner-border spinner-border-sm text-primary" role="status">
      <span class="visually-hidden">Laster...</span>
    </div>
  {/if}
</div>

<style>
  .group-type-heading {
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  .group-list {
    list-style: none;
    padding-left: 0;
    li {
      margin-top: 4px;
    }
  }
</style>
