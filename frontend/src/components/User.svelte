<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type { NestedUserGroupType, NestedUserSchoolType, UserType } from '../generated/types.gen'
  import type { UserDecorated } from '../types/models.d.ts'
  import { usersDestroy } from '../generated/sdk.gen'
  import { addAlert } from '../stores/alerts'
  import GroupTag from './GroupTag.svelte'
  import { formatDate } from '../utils/functions'
  import SinceSchoolStart from './SinceSchoolStart.svelte'
  import Link from './Link.svelte'
  import ButtonMini from './ButtonMini.svelte'

  const { user, decoratedUser, onDeleteUser, onEditUser } = $props<{
    user: UserType
    decoratedUser: UserDecorated
    onDeleteUser: () => Promise<void>
    onEditUser?: () => void
  }>()

  let newestMembership: NestedUserGroupType | null = $derived(
    [...decoratedUser.userGroups].sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )[0]
  )

  const handleDeleteUser = async () => {
    const confirmed = confirm(`Er du sikker på at du vil slette brukeren "${user.name}"?`)
    if (confirmed) {
      await usersDestroy({ path: { id: user.id } })
      addAlert({ type: 'success', message: `Bruker "${user.name}" ble slettet` })
      onDeleteUser()
    }
  }
</script>

<div class="user-grid-row">
  <div>
    <div class="fw-semibold"><Link to="/admin/users/{user.id}">{user.name}</Link></div>
    <div class="text-muted small">{user.email || 'Ingen e-post'}</div>
    <div class="text-muted small">{user.id}</div>
  </div>
  <div>
    <div class="text-muted small">{formatDate(user.createdAt)}</div>
    <SinceSchoolStart dateAsString={user.createdAt} />
  </div>
  <div>
    <div class="text-muted small">
      {#if user.lastActivityAt}
        {formatDate(user.lastActivityAt)}
        <SinceSchoolStart dateAsString={user.lastActivityAt} />
      {:else}
        Ingen aktivitet
      {/if}
    </div>
  </div>
  {#if decoratedUser}
    <div>
      <div class="text-muted small">{formatDate(newestMembership?.createdAt)}</div>
      <SinceSchoolStart dateAsString={newestMembership?.createdAt} />
    </div>

    <!-- User Groups -->
    <div class="small">
      <div class="group-type-heading">Lærer</div>
      <ul class="group-list">
        {#each decoratedUser.teacherGroups as group (group.id)}
          <li>
            <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
          </li>
        {/each}
      </ul>

      <div class="group-type-heading">Elev</div>
      <ul class="group-list">
        {#each decoratedUser.studentGroups as group (group.id)}
          <li>
            <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
          </li>
        {/each}
      </ul>
    </div>

    <!-- User school roles -->
    <div class="mb-1">
      <strong>
        {decoratedUser.userSchools
          .map((userSchool: NestedUserSchoolType) => userSchool.role.name)
          .join(', ') || 'Ingen'}
      </strong>
    </div>

    <div>
      <ButtonMini
        options={{
          title: 'Rediger bruker',
          iconName: 'edit',
          skin: 'tertiary',
          variant: 'icon-only',
          size: 'tiny',
          onClick: () => onEditUser(),
        }}
      />

      <ButtonMini
        options={{
          title: 'Slett bruker',
          iconName: 'trash-can',
          skin: 'tertiary',
          variant: 'icon-only',
          size: 'tiny',
          onClick: () => handleDeleteUser(),
        }}
      />
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
