<script lang="ts">
  import type { GoalCreateType, UserType, SubjectType, GroupType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    usersRetrieve,
    goalsCreate,
    goalsList,
    groupsList,
    subjectsList,
  } from '../generated/sdk.gen'
  import { SUBJECTS_ALLOWED_CUSTOM, GROUP_TYPE_BASIS } from '../utils/constants'
  import { hasUserAccessToFeature } from '../stores/access'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import GoalEdit from '../components/GoalEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import ButtonIcon from '../components/ButtonIcon.svelte'
  import StudentSVG from '../assets/education.svg.svelte'
  import GroupTag from '../components/GroupTag.svelte'
  import { dataStore } from '../stores/data'
  import { trackEvent } from '../stores/analytics'
  import { localStorage } from '../stores/localStorage'

  const { studentId } = $props<{ studentId: string }>()
  const individualGoalcount = 3

  let student = $state<UserType | null>(null)
  let subjects = $state<SubjectType[]>([])
  let groups = $state<GroupType[]>([])
  let { currentSchool, currentUser } = $derived($dataStore)
  let studentGoalsCount = $state<number | undefined>(undefined)

  let goalWip = $state<GoalDecorated | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)

  // Subjects the teacher teaches to this student via their common groups
  const subjectsForGoalEdit = $derived.by(() => {
    if (!student) return $dataStore.subjects
    if (currentUser.isSuperadmin || currentUser.isSchoolAdmin) return $dataStore.subjects
    const teacherGroups: GroupType[] = currentUser?.teacherGroups || []
    const studentGroupIds = student.groupIds || []
    const commonGroups = teacherGroups.filter((g: GroupType) => studentGroupIds.includes(g.id))
    const subjectIds = new Set(commonGroups.map(g => g.subjectId).filter(Boolean))
    const hasSharedBasisGroup = commonGroups.some(g => g.type === GROUP_TYPE_BASIS)
    return $dataStore.subjects.filter(
      s => subjectIds.has(s.id) || (hasSharedBasisGroup && !!s.ownedBySchoolId)
    )
  })

  const fetchStudentData = async (userId: string) => {
    try {
      const userResult = await usersRetrieve({ path: { id: userId } })
      student = userResult.data!

      if (!student) return
      await fetchSubjects(student.id)
      await fetchGroups(student.id)
      await countStudentGoals()
    } catch (error) {
      console.error(`Could not load data for student ${userId}`, error)
    }
  }

  const fetchSubjects = async (studentId: string) => {
    try {
      const subjectsResult = await subjectsList({
        query: { school: currentSchool.id, students: studentId },
      })
      subjects = subjectsResult.data || []
    } catch (error) {
      console.error(`Could not load subjects for ${studentId}`, error)
      subjects = []
    }
  }

  const fetchGroups = async (studentId: string) => {
    try {
      const groupsResult = await groupsList({
        query: { user: studentId, school: currentSchool.id },
      })
      groups = groupsResult.data || []
    } catch (error) {
      console.error(`Could not load groups for ${studentId}`, error)
      groups = []
    }
  }

  const countStudentGoals = async () => {
    const result = await goalsList({ query: { student: studentId, school: currentSchool.id } })
    studentGoalsCount = result.data?.length
  }

  const handleCreateAllIndividualGoals = async () => {
    if (!student || currentSchool.subjectsAllowed !== SUBJECTS_ALLOWED_CUSTOM) return
    const schoolSubjects = $dataStore.subjects
    // This works because schoolSubjects are only custom subjects (not the whole shebang)
    for (const subject of schoolSubjects) {
      for (let i = 0; i < individualGoalcount; i++) {
        const goal: GoalCreateType = {
          studentId: student?.id,
          subjectId: subject.id,
          sortOrder: i + 1,
          masterySchemaId: $dataStore.defaultMasterySchema?.id,
          schoolId: currentSchool.id,
          isRelevant: true,
        }
        await goalsCreate({
          body: goal,
        })
        trackEvent('Goals', 'Create', 'type', 2)
      }
    }

    fetchStudentData(student.id)
  }

  // Remember, we're only editing individual goals here
  const handleEditGoal = async (goal: GoalDecorated | null) => {
    if (!student) return

    if (goal.id) {
      // editing existing goal
      goalWip = {
        ...goal,
        subjectId: goal?.subjectId || localStorage<string>('preferredSubjectId').get(),
        studentId: student.id,
        sortOrder: goal?.sortOrder,
        masterySchemaId: goal?.masterySchemaId || $dataStore.defaultMasterySchema?.id,
      }
    } else {
      // new goal
      goalWip = {
        studentId: student.id,
        isIndividual: true,
        masterySchemaId: $dataStore.defaultMasterySchema?.id,
        schoolId: currentSchool.id,
        isRelevant: true,
      }
    }
    isGoalEditorOpen = true
  }

  const handleCloseEditGoal = () => {
    isGoalEditorOpen = false
    goalWip = null
    fetchStudentData(studentId)
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
      <div class="student-svg" title="Elev" aria-hidden="true">
        <StudentSVG />
      </div>
      <div>
        <h2 class="mb-0" title="Fornavn">
          {student.name.split(' ')[0]}
        </h2>
        <div class="mt-0 text-secondary" title="Etternavn">
          {student.name.split(' ').slice(1).join(' ')}
        </div>
      </div>
    </div>
    <div class="my-3">
      {#each groups as group}
        <span class="me-2">
          <GroupTag
            {group}
            isGroupNameEnabled={true}
            href={`/groups/${group.id}/`}
            classes="mb-2"
          />
        </span>
      {/each}
    </div>

    <!-- Goals and mastery -->
    <div class="card shadow-sm">
      <div class="d-flex align-items-center gap-2 card-header">
        <h2>Mål</h2>
        {#if $hasUserAccessToFeature( 'goal', 'create', { studentId: student.id, studentGroupIds: student.groupIds } )}
          {#if studentGoalsCount === 0 && currentSchool.subjectsAllowed === SUBJECTS_ALLOWED_CUSTOM}
            <ButtonMini
              options={{
                iconName: 'goal',
                classes: 'm-2',
                title: `Opprett ${individualGoalcount} individuelle mål for hvert fag`,
                onClick: () => handleCreateAllIndividualGoals(),
                variant: 'icon-left',
                skin: 'primary',
              }}
            >
              Opprett {individualGoalcount} individuelle mål for hvert fag
            </ButtonMini>
          {:else}
            <ButtonIcon
              options={{
                iconName: 'goal',
                classes: 'bordered ms-1',
                title: 'Legg til nytt individuelt mål',
                onClick: () => handleEditGoal({}),
              }}
            />
          {/if}
        {/if}
      </div>

      {#if subjects.length > 0}
        <ul class="list-group list-group-flush">
          {#each subjects as subject (subject.id)}
            <li class="list-group-item py-3">
              <StudentSubjectGoals
                {subject}
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
<Offcanvas bind:isOpen={isGoalEditorOpen} ariaLabel="Rediger mål" onClosed={handleCloseEditGoal}>
  {#if goalWip}
    <GoalEdit
      goal={goalWip}
      {student}
      subjects={subjectsForGoalEdit}
      isGoalIndividual={true}
      onDone={handleCloseEditGoal}
    />
  {/if}
</Offcanvas>

<style>
  .student-svg > :global(svg) {
    height: 7rem;
  }
</style>
