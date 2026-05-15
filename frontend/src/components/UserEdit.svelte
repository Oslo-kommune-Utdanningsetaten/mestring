<script lang="ts">
  import {
    usersCreate,
    usersPartialUpdate,
    userSchoolsCreate,
    userSchoolsDestroy,
  } from '../generated/sdk.gen'
  import type { SchoolType, UserCreateType, NestedUserSchoolType } from '../generated/types.gen'
  import type { UserDecorated } from '../types/models.d.ts'
  import { dataStore } from '../stores/data'
  import { addAlert } from '../stores/alerts'
  import { USER_ROLES } from '../utils/constants'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import ButtonMini from './ButtonMini.svelte'
  import { tr } from 'date-fns/locale'

  const { user, school, onDone } = $props<{
    user: Partial<UserDecorated>
    school: SchoolType
    onDone?: () => void | Promise<void>
  }>()

  const userSchoolRoleNames = [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN]
  const userSchoolRoles = $derived(
    $dataStore.roles.filter(role => userSchoolRoleNames.includes(role.name as any))
  )

  let localUser = $state<Partial<UserDecorated>>({ ...user })

  let localRoleIds = $state<Set<string>>(
    new Set<string>(
      (user.userSchools ?? ([] as NestedUserSchoolType[]))
        .filter(
          (us: NestedUserSchoolType) =>
            us.school.id === school.id && userSchoolRoleNames.includes(us.role.name as any)
        )
        .map((us: NestedUserSchoolType) => us.role.id)
    )
  )

  let isSaving = $state(false)

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

  const toggleRole = (roleId: string) => {
    const next = new Set(localRoleIds)
    if (next.has(roleId)) {
      next.delete(roleId)
    } else {
      next.add(roleId)
    }
    localRoleIds = next
  }

  const reconcileUserSchoolRoles = async (userId: string) => {
    const existingUserSchools = (localUser.userSchools ?? ([] as NestedUserSchoolType[])).filter(
      (userSchool: NestedUserSchoolType) =>
        userSchool.school.id === school.id &&
        userSchoolRoleNames.includes(userSchool.role.name as any)
    )
    const existingRoleIds = new Set(
      existingUserSchools.map((us: NestedUserSchoolType) => us.role.id)
    )

    const toRemove = existingUserSchools.filter(
      (us: NestedUserSchoolType) => !localRoleIds.has(us.role.id)
    )
    const toAdd = [...localRoleIds].filter(roleId => !existingRoleIds.has(roleId))

    await Promise.all([
      ...toRemove.map((us: NestedUserSchoolType) => userSchoolsDestroy({ path: { id: us.id } })),
      ...toAdd.map(roleId => userSchoolsCreate({ body: { userId, schoolId: school.id, roleId } })),
    ])
  }

  const handleSave = async () => {
    if (!isFormValid) return
    isSaving = true
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
        await reconcileUserSchoolRoles(localUser.id)
        addAlert({ type: 'success', message: `Bruker "${localUser.name}" ble oppdatert` })
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

        await reconcileUserSchoolRoles(newUser.id)
        addAlert({ type: 'success', message: `Bruker "${newUser.name}" ble opprettet` })
      }
      if (onDone) await onDone()
    } catch (error) {
      console.error('Error saving user:', error)
      addAlert({ type: 'danger', message: 'Noe gikk galt ved lagring av bruker' })
    } finally {
      isSaving = false
    }
  }
</script>

<div class="user-edit p-4">
  <h3 class="pb-2">{localUser.id ? `Editing user: ${localUser.name}` : 'New user'}</h3>
  <hr />

  <!-- Name -->
  <div class="form-group mb-3">
    <label for="name" class="form-label">Navn</label>
    <input
      id="newUserName"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localUser.name}
      placeholder="Fornavn Etternavn"
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
      placeholder="brukernavn@osloskolen.no"
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
      placeholder="brukernavn@feide.osloskolen.no"
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
          checked={localRoleIds.has(role.id)}
          onchange={() => toggleRole(role.id)}
        ></pkt-checkbox>
      </div>
    {/each}
  </div>

  <div class="d-flex gap-3 justify-content-start mt-5">
    <ButtonMini
      options={{
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        disabled: !isFormValid || isSaving,
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
</style>
