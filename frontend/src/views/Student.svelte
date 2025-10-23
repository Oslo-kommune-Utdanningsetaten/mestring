<script lang="ts">
  import type { GoalCreateType, UserType, SubjectType } from '../generated/types.gen'
  import { usersRetrieve, goalsCreate, goalsList } from '../generated/sdk.gen'
  import { subjectIdsViaGroupOrGoal } from '../utils/functions'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import GoalEdit from '../components/GoalEdit.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import StudentSVG from '../assets/education.svg.svelte'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserType | null>(null)
  let subjects = $state<SubjectType[]>([])
  let currentSchool = $derived($dataStore.currentSchool)
  let goalWip = $state<GoalDecorated | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)
  let studentGoalsCount = $state<number>(0)

  const fetchStudentData = async (userId: string) => {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      if (!student) return
      await fetchSubjects(student.id)
      await countStudentGoals()
    } catch (error) {
      console.error(`Could not load data for student ${userId}`, error)
    }
  }

  const fetchSubjects = async (studentId: string) => {
    try {
      const subjectIds = await subjectIdsViaGroupOrGoal(studentId, currentSchool.id)
      if (subjectIds.length > 0) {
        subjects = $dataStore.subjects.filter((subject: SubjectType) =>
          subjectIds.includes(subject.id)
        )
      }
    } catch (error) {
      console.error(`Could not load subjects for ${studentId}`, error)
      subjects = []
    }
  }

  const countStudentGoals = async () => {
    const result = await goalsList({ query: { student: studentId } })
    studentGoalsCount = result.data?.length || 0
  }

  const handleCreateAllPersonalGoals = async () => {
    if (!student) return
    const preferredMasterySchemaId =
      (getLocalStorageItem('preferredMasterySchemaId') as string) ||
      $dataStore.masterySchemas[0]?.id
    const schoolSubjects = $dataStore.subjects
    schoolSubjects.forEach(async (subject, index) => {
      for (let i = 0; i < 3; i++) {
        const goal: GoalCreateType = {
          studentId: student?.id,
          subjectId: subject.id,
          sortOrder: i + 1,
          masterySchemaId: preferredMasterySchemaId,
        }
        await goalsCreate({
          body: goal,
        })
      }
    })

    fetchStudentData(student.id)
  }

  // Add personal goal
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
    fetchStudentData(studentId)
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
    <div class="d-flex align-items-center gap-3">
      <div class="student-svg" title="Elev">
        <StudentSVG />
      </div>
      <div>
        <h1 class="mb-0" title="Fornavn">
          {student.name.split(' ')[0]}
        </h1>
        <h5 class="mt-0 text-secondary" title="Etternavn">
          {student.name.split(' ').slice(1).join(' ')}
        </h5>
      </div>
    </div>
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
        {#if studentGoalsCount === 0}
          <ButtonMini
            options={{
              iconName: 'plus-sign',
              classes: 'm-2',
              title: 'Opprett alle mål!',
              onClick: () => handleCreateAllPersonalGoals(),
              variant: 'icon-left',
              skin: 'primary',
            }}
          >
            Opprett alle mål!
          </ButtonMini>
        {/if}
      </div>
      {#if subjects.length > 0}
        <ul class="list-group list-group-flush">
          {#each subjects as subject (subject.id)}
            <li class="list-group-item py-3">
              <StudentSubjectGoals
                subjectId={subject.id}
                {student}
                onRefreshRequired={() => fetchStudentData(studentId)}
              />
            </li>
          {/each}
        </ul>
      {:else}
        <div class="alert alert-info m-2">Ingen mål for denne eleven</div>
      {/if}
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
  .student-svg > :global(svg) {
    height: 7rem;
  }
</style>
