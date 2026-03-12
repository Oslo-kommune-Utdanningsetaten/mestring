<script lang="ts">
  import { dataStore } from '../../stores/data'
  import { USER_ROLES } from '../../utils/constants'
  import { usersList } from '../../generated/sdk.gen'
  import type { GroupType, UserType } from '../../generated/types.gen'
  import GroupTag from '../../components/GroupTag.svelte'
  import UserTag from '../../components/UserTag.svelte'
  import Link from '../../components/Link.svelte'
  import ObservationsBarChart from '../../components/ObservationsBarChart.svelte'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])
  let groupMembers = $state<Record<string, { teachers: UserType[]; students: UserType[] }>>({})

  const fetchAllGroupMembers = async () => {
    groups.forEach(async group => {
      try {
        const teachersResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: USER_ROLES.TEACHER },
        })
        const studentsResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: USER_ROLES.STUDENT },
        })
        const teachers = teachersResult.data || []
        const students = studentsResult.data || []
        groupMembers = { ...groupMembers, [group.id]: { teachers, students } }
      } catch (error) {
        console.error(`Error fetching members for group ${group.id}:`, error)
        groupMembers = { ...groupMembers, [group.id]: { teachers: [], students: [] } }
      }
    })
  }

  const getSubjectName = (subjectId: string) => {
    const subject = $dataStore.subjects.find(subj => subj.id === subjectId)
    return subject ? subject.displayName : 'Ukjent fag'
  }

  $effect(() => {
    if (currentSchool) {
      fetchAllGroupMembers()
    }
  })
</script>

<section class="pt-3">
  <h2 class="mb-4">Statistikk for {currentSchool?.displayName}</h2>
  <div class="border border-3 mb-4 p-3">
    <h3 class="mb-2">Hele skolen</h3>
    <!-- Observations for whole school -->
    <ObservationsBarChart schoolId={currentSchool.id} width={300} height={150} />
  </div>

  {#if groups.length > 1}
    {#each groups as group}
      <div class="border border-3 mb-4 p-3">
        <h3 class="mb-2" title={group.feideId}>
          <Link to="/groups/{group.id}">
            {group.displayName}
          </Link>
        </h3>
        <GroupTag classes="mb-1" {group} isGroupTypeNameEnabled={true} />

        {#if group.subjectId}
          <div class="text-muted">
            {getSubjectName(group.subjectId)}
          </div>
        {/if}

        <!-- students -->
        <div class="mt-2 mb-1">
          <!-- Observations for group -->
          <ObservationsBarChart groupId={group.id} width={300} height={150} />
        </div>
      </div>
    {/each}
  {/if}
</section>

<style>
</style>
