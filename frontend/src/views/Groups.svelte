<script lang="ts">
  import { dataStore } from '../stores/data'
  import { urlStringFrom, abbreviateName } from '../utils/functions'
  import { TEACHER_ROLE, STUDENT_ROLE } from '../utils/constants'
  import { groupsList, usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType } from '../generated/types.gen'
  import GroupTypeTag from '../components/GroupTypeTag.svelte'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $state<GroupType[]>([])
  let groupMembers = $state<Record<string, { teachers: UserType[]; students: UserType[] }>>({})

  const fetchGroups = async () => {
    try {
      const result = await groupsList({
        query: { school: currentSchool?.id, enabled: 'only' },
      })
      groups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      groups = []
    }
  }

  const fetchAllGroupMembers = async () => {
    groups.forEach(async group => {
      try {
        const teachersResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: TEACHER_ROLE },
        })
        const studentsResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: STUDENT_ROLE },
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
      fetchGroups().then(() => {
        fetchAllGroupMembers()
      })
    }
  })
</script>

<section class="py-3">
  <h2>Mine grupper</h2>

  {#if groups.length === 0}
    <div class="mt-3">
      🫤 Du har visst ikke tilgang til noen grupper på {currentSchool?.displayName}.
    </div>
  {:else}
    {#each groups as group}
      <div class="card shadow-sm p-3">
        <h3 class="mt-1 mb-3" title={group.feideId}>
          <a href="/groups/{group.id}">
            {group.displayName}
          </a>
        </h3>

        <div class="d-flex align-items-center gap-2">
          <GroupTypeTag {group} />

          <!-- teachers -->
          {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
            {#each groupMembers[group.id].teachers as teacher}
              <pkt-tag iconName="lecture" skin="yellow">
                <span title={teacher.feideId}>{abbreviateName(teacher.name)}</span>
              </pkt-tag>
            {/each}
          {/if}
        </div>

        {#if group.subjectId}
          <div class="mt-3">
            {getSubjectName(group.subjectId)}
          </div>
        {/if}

        <!-- students -->
        <div class="mt-3 mb-1">
          {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
            {#if currentSchool.isStudentListEnabled || $dataStore.isSuperadmin || $dataStore.isSchoolAdmin || $dataStore.isSchoolInspector}
              <a
                href={urlStringFrom(
                  { groupId: group.id },
                  {
                    path: '/students',
                    mode: 'replace',
                  }
                )}
              >
                {groupMembers[group.id].students.length}
                {groupMembers[group.id].students.length === 1 ? 'elev' : 'elever'}
              </a>
            {:else}
              {groupMembers[group.id].students.length}
              {groupMembers[group.id].students.length === 1 ? 'elev' : 'elever'}
            {/if}
          {:else}
            <div class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Henter data...</span>
            </div>
          {/if}
        </div>
      </div>
    {/each}
  {/if}
</section>

<style>
</style>
