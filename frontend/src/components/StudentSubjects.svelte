<script lang="ts">
  import type { UserType, GroupType, SubjectType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { groupsList } from '../generated/sdk.gen'
  import { fetchGoalsForSubjectAndStudent } from '../utils/functions'
  import StudentSubject from './StudentSubject.svelte'

  const { student } = $props<{
    student: UserType
  }>()

  let { currentSchool, subjects } = $derived($dataStore)
  let groups = $state<GroupType[]>([])
  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let studentSubjects = $state<SubjectType[]>([])
  let isLoading = $state(true)

  const fetchData = async () => {
    try {
      const groupsResult = await groupsList({
        query: { school: currentSchool.id, user: student.id },
      })
      groups = (groupsResult.data || []).filter(group => group.type === 'teaching')
    } catch (error) {
      console.error(`Could not load subjects for ${student.id}`, error)
      groups = []
      isLoading = false
      return
    }
    studentSubjects = subjects.filter(subject =>
      groups.some(group => group.subjectId === subject.id)
    )

    await Promise.all(
      studentSubjects.map(async subject => {
        const goals = await fetchGoalsForSubjectAndStudent(
          subject.id,
          student.id,
          currentSchool?.id!,
          student.allGroups
        )
        goalsBySubjectId = { ...goalsBySubjectId, [subject.id]: goals }
      })
    )
    isLoading = false
  }

  $effect(() => {
    if (currentSchool) {
      fetchData()
    }
  })
</script>

<section class="py-4">
  <h2>Mine fag</h2>
  {#if isLoading}
    <div class="spinner-border spinner-border-sm" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
  {:else if groups.length < 1}
    <div class="mt-3">🫤 Ingen fag, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4 list-group">
      {#each groups as group (group.id)}
        {@const subject = studentSubjects.find(s => s.id === group.subjectId)}
        {#if subject}
          <div class="list-group-item">
            <StudentSubject {student} {subject} goals={goalsBySubjectId[subject.id]} />
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</section>

<style>
</style>
