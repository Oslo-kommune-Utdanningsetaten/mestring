<script lang="ts">
  import type { GoalCreateType, UserType, SubjectType, GroupType } from '../generated/types.gen'
  import {
    usersRetrieve,
    goalsCreate,
    goalsList,
    groupsList,
    subjectsList,
  } from '../generated/sdk.gen'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import Link from '../components/Link.svelte'
  import StudentSVG from '../assets/education.svg.svelte'
  import { dataStore } from '../stores/data'

  const { studentId } = $props<{ studentId: string }>()
  const individualGoalcount = 3
  let student = $state<UserType | null>(null)
  let subjects = $state<SubjectType[]>([])
  let groups = $state<GroupType[]>([])
  let currentSchool = $derived($dataStore.currentSchool)
  let studentGoalsCount = $state<number>(0)

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
    const result = await goalsList({ query: { student: studentId } })
    studentGoalsCount = result.data?.length || 0
  }

  const handleCreateAllPersonalGoals = async () => {
    if (!student) return
    const schoolSubjects = $dataStore.subjects
    schoolSubjects.forEach(async (subject, index) => {
      for (let i = 0; i < individualGoalcount; i++) {
        const goal: GoalCreateType = {
          studentId: student?.id,
          subjectId: subject.id,
          sortOrder: i + 1,
          masterySchemaId: $dataStore.defaultMasterySchema?.id,
          schoolId: $dataStore.currentSchool.id,
          isRelevant: true,
        }
        await goalsCreate({
          body: goal,
        })
      }
    })

    fetchStudentData(student.id)
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
    <div class="my-4">
      Medlem av:
      {#each groups as group, index (group.id)}
        <span>
          <Link to={`/groups/${group.id}/`}>
            {group.displayName}
          </Link>{index < groups.length - 1 ? ', ' : ''}
        </span>
      {/each}
    </div>

    <!-- Goals and mastery -->
    <div class="card shadow-sm">
      <div class="d-flex align-items-center gap-2 mb-3 card-header">
        <h2>Mål</h2>
        {#if studentGoalsCount === 0}
          <ButtonMini
            options={{
              iconName: 'goal',
              classes: 'm-2',
              title: `Opprett ${individualGoalcount} individuelle mål for hvert fag`,
              onClick: () => handleCreateAllPersonalGoals(),
              variant: 'icon-left',
              skin: 'primary',
            }}
          >
            Opprett {individualGoalcount} individuelle mål for hvert fag
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

<style>
  .student-svg > :global(svg) {
    height: 7rem;
  }
</style>
