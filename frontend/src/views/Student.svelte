<script lang="ts">
  import type { GroupReadable, UserReadable, SubjectReadable } from '../generated/types.gen'
  import { usersRetrieve, groupsList } from '../generated/sdk.gen'
  import { subjectIdsViaGroupOrGoal } from '../utils/functions'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import GoalEdit from '../components/GoalEdit.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let groups = $state<GroupReadable[] | []>([])
  let subjects = $state<SubjectReadable[]>([])
  let currentSchool = $derived($dataStore.currentSchool)
  let goalWip = $state<GoalDecorated | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)

  const fetchStudentData = async (userId: string) => {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      if (!student) return
      await fetchGroupsForStudent(student.id)
      await fetchSubjects(student.id)
    } catch (error) {
      console.error(`Could not load data for student ${userId}`, error)
    }
  }

  const fetchGroupsForStudent = async (studentId: string) => {
    try {
      const userGroups: any = await groupsList({
        query: { user: studentId, roles: 'student', school: currentSchool.id, isEnabled: true },
      })
      groups = userGroups.data || []
    } catch (error) {
      console.error(`Could not load groups for ${studentId}`, error)
      groups = []
    }
  }

  const fetchSubjects = async (studentId: string) => {
    try {
      const subjectIds = await subjectIdsViaGroupOrGoal(studentId, currentSchool.id)
      if (subjectIds.length > 0) {
        subjects = $dataStore.subjects.filter((subject: SubjectReadable) =>
          subjectIds.includes(subject.id)
        )
      }
    } catch (error) {
      console.error(`Could not load subjects for ${studentId}`, error)
      subjects = []
    }
  }

  // Add personal goals
  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      subjectId: null,
      studentId: student?.id,
      sortOrder: goal?.sortOrder || 1,
      masterySchemaId:
        goal?.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
    }
    isGoalEditorOpen = true
  }

  const handleCloseEditGoal = () => {
    isGoalEditorOpen = false
  }

  const handleGoalDone = async () => {
    handleCloseEditGoal()
  }

  $effect(() => {
    if (currentSchool && currentSchool.id) {
      fetchStudentData(studentId)
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h1>Elev: {student.name}</h1>

    <!-- Goals and mastery -->
    <div class="card shadow-sm">
      <div class="d-flex align-items-center gap-2 mb-3 card-header">
        <h2>Mål</h2>
        <ButtonMini
          options={{
            iconName: 'plus-sign',
            classes: 'mini-button bordered',
            title: 'Legg til nytt personlig mål',
            onClick: () => handleEditGoal(null),
          }}
        />
      </div>
      {#if subjects.length > 0}
        <ul class="list-group list-group-flush">
          {#each subjects as subject (subject.id)}
            <li class="list-group-item py-3">
              <StudentSubjectGoals subjectId={subject.id} {student} />
            </li>
          {/each}
        </ul>
      {:else}
        <div class="alert alert-info m-2">Ingen mål for denne eleven</div>
      {/if}
    </div>

    <!-- Groups -->
    <div class="card shadow-sm">
      <h2 class="card-header">Medlem av</h2>
      <div class="card-body">
        {#if groups}
          <ul class="mb-0">
            {#each groups as group}
              <li>
                <a href={`/groups/${group.id}`}>
                  {group.displayName}
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="alert alert-danger">Ikke medlem av noen grupper</div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="m-2">Fant ikke eleven</div>
  {/if}
</section>

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isGoalEditorOpen}
  ariaLabel="Rediger mål"
  onClosed={() => {
    goalWip = null
    fetchStudentData(studentId)
  }}
>
  {#if goalWip}
    <GoalEdit
      goal={goalWip}
      {student}
      subject={null}
      isGoalPersonal={true}
      onDone={handleGoalDone}
    />
  {/if}
</Offcanvas>

<style>
</style>
