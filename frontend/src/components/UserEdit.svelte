<script lang="ts">
  import {
    usersCreate,
    usersPartialUpdate,
    userSchoolsCreate,
    userSchoolsDestroy,
    userGroupsCreate,
    userGroupsDestroy,
    groupsList,
  } from '../generated/sdk.gen'
  import type {
    SchoolType,
    UserCreateType,
    NestedUserSchoolType,
    NestedUserGroupType,
    GroupType,
  } from '../generated/types.gen'
  import type { UserDecorated } from '../types/models.d.ts'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import { dataStore } from '../stores/data'
  import { addAlert } from '../stores/alerts'
  import { USER_ROLES } from '../utils/constants'
  import { getPreferredCreatedParams } from '../utils/functions'
  import { GROUP_VALIDITY_OPTIONS } from '../utils/constants'
  import { localStorage } from '../stores/localStorage'
  import ButtonMini from './ButtonMini.svelte'

  const preferredGroupValidity = localStorage<GROUP_VALIDITY_OPTIONS>('preferredGroupValidity')
  const groupValidity = $derived($preferredGroupValidity || GROUP_VALIDITY_OPTIONS.ONLY)

  const { user, school, onDone } = $props<{
    user: Partial<UserDecorated>
    school: SchoolType
    onDone?: () => void | Promise<void>
  }>()

  const userSchoolRoleNames = [USER_ROLES.STAFF, USER_ROLES.INSPECTOR, USER_ROLES.ADMIN]
  const userGroupRoleNames = [USER_ROLES.TEACHER, USER_ROLES.STUDENT]

  const userSchoolRoles = $derived(
    $dataStore.roles.filter(role => userSchoolRoleNames.includes(role.name as any))
  )

  let localUser = $state<Partial<UserDecorated>>({ ...user })

  let updatedUserSchoolRoleIds = $state<string[]>(
    (user.userSchools ?? ([] as NestedUserSchoolType[]))
      .filter(
        (us: NestedUserSchoolType) =>
          us.school.id === school.id && userSchoolRoleNames.includes(us.role.name as any)
      )
      .map((us: NestedUserSchoolType) => us.role.id)
  )

  const userGroupRoles = $derived(
    $dataStore.roles.filter(role => userGroupRoleNames.includes(role.name as any))
  )

  // Record of groupId -> roleId[] reflecting local membership state
  let updatedRoleIdsByGroupId = $state<Record<string, string[]>>({
    ...(user.userGroups
      ? Object.fromEntries(
          user.userGroups.map((ug: NestedUserGroupType) => [ug.group.id, [ug.role.id]])
        )
      : {}),
  })

  // Stable list of group IDs the user already belongs to (for initial sort order)
  const initialMemberGroupIds = (user.userGroups ?? ([] as NestedUserGroupType[])).map(
    (ug: NestedUserGroupType) => ug.group.id
  )

  let schoolGroups = $state<GroupType[]>([])
  let isLoadingGroups = $state(true)

  const fetchSchoolGroups = async () => {
    try {
      const result = await groupsList({
        query: {
          school: school.id,
          enabled: 'only',
          valid: groupValidity,
          ...getPreferredCreatedParams(),
        },
      })
      schoolGroups = result.data || []
    } catch (e) {
      console.error('Error fetching groups:', e)
    } finally {
      isLoadingGroups = false
    }
  }

  const sortedSchoolGroups = $derived(
    [...schoolGroups].sort((a, b) => {
      const aHas = initialMemberGroupIds.includes(a.id) ? 0 : 1
      const bHas = initialMemberGroupIds.includes(b.id) ? 0 : 1
      if (aHas !== bHas) return aHas - bHas
      return a.displayName.localeCompare(b.displayName)
    })
  )

  let isFormValid = $derived(
    !!localUser.name?.trim() && !!localUser.feideId?.trim() && !!localUser.email?.trim()
  )

  const handleEmailBlur = () => {
    if (localUser.email) {
      localUser.feideId = localUser.email.replace('@osloskolen.no', '@feide.osloskolen.no')
    } else {
      localUser.feideId = ''
    }
    localUser = { ...localUser }
  }

  const toggleUserGroupMembership = (groupId: string, roleId: string) => {
    const next = { ...updatedRoleIdsByGroupId }
    const roles = next[groupId] ?? []
    const updatedRoleIds = roles.includes(roleId)
      ? roles.filter(id => id !== roleId)
      : [...roles, roleId]
    if (updatedRoleIds.length === 0) {
      delete next[groupId]
    } else {
      next[groupId] = updatedRoleIds
    }
    updatedRoleIdsByGroupId = { ...next }
  }

  const reconcileUserGroupMemberships = async (userId: string) => {
    const existingUserGroups = localUser.userGroups || []

    const userGroupIdsToDelete = existingUserGroups
      .filter(
        (ug: NestedUserGroupType) => !updatedRoleIdsByGroupId[ug.group.id]?.includes(ug.role.id)
      )
      .map((ug: NestedUserGroupType) => ug.id)

    const membershipsToAdd = Object.entries(updatedRoleIdsByGroupId)
      .flatMap(([groupId, roleIds]) =>
        roleIds.map(roleId => {
          const alreadyExists = existingUserGroups.some(
            (ug: NestedUserGroupType) => ug.group.id === groupId && ug.role.id === roleId
          )
          return alreadyExists ? null : { groupId, roleId }
        })
      )
      .filter((x): x is { groupId: string; roleId: string } => x !== null)

    await Promise.all([
      ...userGroupIdsToDelete.map((id: string) => userGroupsDestroy({ path: { id } })),
      ...membershipsToAdd.map(({ groupId, roleId }) =>
        userGroupsCreate({ body: { userId, groupId, roleId } as any })
      ),
    ])
  }

  const toggleUserSchoolRole = (roleId: string) => {
    if (updatedUserSchoolRoleIds.includes(roleId)) {
      updatedUserSchoolRoleIds = updatedUserSchoolRoleIds.filter(id => id !== roleId)
    } else {
      updatedUserSchoolRoleIds = [...updatedUserSchoolRoleIds, roleId]
    }
  }

  const reconcileUserSchoolRoles = async (userId: string) => {
    const existingUserSchools = (localUser.userSchools ?? ([] as NestedUserSchoolType[])).filter(
      (userSchool: NestedUserSchoolType) =>
        userSchool.school.id === school.id &&
        userSchoolRoleNames.includes(userSchool.role.name as any)
    )
    const existingRoleIds = existingUserSchools.map((us: NestedUserSchoolType) => us.role.id)

    const toRemove = existingUserSchools.filter(
      (us: NestedUserSchoolType) => !updatedUserSchoolRoleIds.includes(us.role.id)
    )
    const toAdd = updatedUserSchoolRoleIds.filter(roleId => !existingRoleIds.includes(roleId))

    await Promise.all([
      ...toRemove.map((us: NestedUserSchoolType) => userSchoolsDestroy({ path: { id: us.id } })),
      ...toAdd.map(roleId => userSchoolsCreate({ body: { userId, schoolId: school.id, roleId } })),
    ])
  }

  const handleSave = async () => {
    if (!isFormValid) return
    let message = localUser.id
      ? `Bruker "${localUser.name}" oppdatert`
      : `Bruker "${localUser.name}" opprettet`
    let userId = localUser.id
    try {
      if (localUser.id) {
        // update user
        await usersPartialUpdate({
          path: { id: localUser.id! },
          body: {
            name: localUser.name!.trim(),
            feideId: localUser.feideId!.trim(),
            email: localUser.email!.trim(),
          },
        })
      } else {
        // create user
        const userBody: UserCreateType = {
          name: localUser.name!.trim(),
          feideId: localUser.feideId!.trim(),
          email: localUser.email!.trim(),
        }
        const result = await usersCreate({ body: userBody })
        const newUser = result.data
        if (!newUser) throw new Error('No user returned from API')
        userId = newUser.id
      }
      await Promise.all([reconcileUserSchoolRoles(userId), reconcileUserGroupMemberships(userId)])
      addAlert({ type: 'success', message })
      if (onDone) await onDone()
    } catch (error) {
      console.error('Error saving user:', error)
      addAlert({ type: 'danger', message: 'Noe gikk galt ved lagring av bruker' })
    }
  }

  $effect(() => {
    fetchSchoolGroups()
  })
</script>

<div class="user-edit p-4">
  <h3 class="pb-2">{localUser.id ? `Editing user: ${localUser.name}` : 'New user'}</h3>
  <hr />

  <!-- Name -->
  <div class="form-group mb-3">
    <label for="name" class="form-label">Navn</label>
    <input
      id="name"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localUser.name}
      placeholder="Tina Snips"
      required={true}
    />
  </div>

  <!-- Email -->
  <div class="form-group mb-3">
    <label for="email" class="form-label">E-post</label>
    <input
      id="email"
      type="email"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localUser.email}
      onblur={handleEmailBlur}
      placeholder="tinsni001@osloskolen.no"
      required={true}
    />
  </div>

  <!-- FeideId, automatically updated based on email -->
  <div class="form-group mb-3">
    <label for="feideid" class="form-label">Feide-ID</label>
    <input
      id="feideid"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localUser.feideId}
      disabled={true}
      placeholder="tinsni001@feide.osloskolen.no"
    />
  </div>

  <!-- User School roles -->
  <div class="form-group mb-3">
    <p class="form-label fw-bold mb-2">Roller ved {school?.displayName}</p>
    {#each userSchoolRoles as role}
      <div class="mb-2">
        <pkt-checkbox
          label={role.name}
          labelPosition="right"
          isSwitch="true"
          checked={updatedUserSchoolRoleIds.includes(role.id)}
          onchange={() => toggleUserSchoolRole(role.id)}
        ></pkt-checkbox>
      </div>
    {/each}
  </div>

  <!-- User Group memberships -->
  <div class="form-group my-3">
    <p class="form-label fw-bold">Gruppemedlemskap ved {school?.displayName}</p>
    {#if isLoadingGroups}
      <p class="text-muted">Laster grupper...</p>
    {:else}
      <div class="group-memberships">
        <div class="group-memberships-header d-flex align-items-center mb-1">
          <div class="flex-grow-1"></div>
          {#each userGroupRoles as role}
            <div class="group-role-col text-center">
              <small class="fw-bold">{role.name === USER_ROLES.TEACHER ? 'Lærer' : 'Elev'}</small>
            </div>
          {/each}
        </div>
        {#each sortedSchoolGroups as group}
          <div class="group-row d-flex align-items-center mb-1">
            <span class="flex-grow-1 text-truncate">{group.displayName}</span>
            {#each userGroupRoles as role}
              <div class="group-role-col text-center">
                <pkt-checkbox
                  isSwitch="true"
                  checked={!!updatedRoleIdsByGroupId[group.id]?.includes(role.id)}
                  onchange={() => toggleUserGroupMembership(group.id, role.id)}
                ></pkt-checkbox>
              </div>
            {/each}
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <div class="d-flex gap-3 justify-content-start mt-5">
    <ButtonMini
      options={{
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        disabled: !isFormValid,
        onClick: () => handleSave(),
      }}
    >
      {localUser.id ? 'Lagre' : 'Opprett bruker'}
    </ButtonMini>

    <ButtonMini
      options={{
        title: 'Avbryt',
        iconName: 'close',
        skin: 'secondary',
        variant: 'label-only',
        onClick: () => onDone?.(),
      }}
    >
      Avbryt
    </ButtonMini>
  </div>
</div>

<style>
  label {
    font-weight: 800;
  }

  .input-field {
    height: 48px;
  }

  input {
    width: 100% !important;
  }

  .group-role-col {
    width: 56px;
    flex-shrink: 0;
  }

  .group-memberships {
    max-height: 400px;
    overflow-y: auto;
  }
</style>
