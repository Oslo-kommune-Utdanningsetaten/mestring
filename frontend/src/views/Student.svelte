<script lang="ts">
  import type { GoalCreateType, UserType, SubjectType, GroupType } from '../generated/types.gen'
  import {
    usersRetrieve,
    goalsCreate,
    goalsList,
    groupsList,
    subjectsList,
  } from '../generated/sdk.gen'

  import {
    getPreferredCreatedParams,
    getPreferredGroupValidity,
  } from '../stores/localStorageFunctions'
  import { SUBJECTS_ALLOWED_CUSTOM } from '../utils/constants'
  import { dataStore } from '../stores/data'
  import { trackEvent } from '../stores/analytics'
  import type { AppData } from '../types/models'

  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import GoalWidgets from '../components/edit/GoalWidgets.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import GroupTag from '../components/GroupTag.svelte'
  import StudentSVG from '../assets/education.svg.svelte'

  const { studentId } = $props<{ studentId: string }>()
  const individualGoalcount = 3

  let student = $state<UserType | undefined>(undefined)
  let subjects = $state<SubjectType[]>([])
  let groups = $state<GroupType[]>([])
  let { currentSchool } = $derived($dataStore) satisfies AppData
  let individualStudentGoalsCount = $state<number | undefined>(undefined)

  const fetchStudentData = async () => {
    try {
      const userResult = await usersRetrieve({ path: { id: studentId } })
      student = userResult.data!

      if (!student) return
      await fetchSubjects()
      await fetchGroups()
      await countStudentGoals()
    } catch (error) {
      console.error(`Could not load data for student ${studentId}`, error)
    }
  }

  const fetchSubjects = async () => {
    try {
      const subjectsResult = await subjectsList({
        query: { school: currentSchool.id, students: studentId },
      })
      subjects = subjectsResult.data || []
      if (subjects.length === 0 && currentSchool.subjectsAllowed === SUBJECTS_ALLOWED_CUSTOM) {
        // No subjects for this student, but since school allows custom subjects display all those subjects
        subjects = $dataStore.subjects.filter(
          subject => subject.ownedBySchoolId === currentSchool.id
        )
      }
    } catch (error) {
      console.error(`Could not load subjects for ${studentId}`, error)
      subjects = []
    }
  }

  const fetchGroups = async () => {
    try {
      const groupsResult = await groupsList({
        query: { user: studentId, school: currentSchool.id, valid: getPreferredGroupValidity() },
      })
      groups = groupsResult.data || []
    } catch (error) {
      console.error(`Could not load groups for ${studentId}`, error)
      groups = []
    }
  }

  const countStudentGoals = async () => {
    const result = await goalsList({
      query: { student: studentId, school: currentSchool.id, ...getPreferredCreatedParams() },
    })
    individualStudentGoalsCount = (result.data || []).filter(g => g.isIndividual).length
  }

  // Creates a hard coded number of individual goals for each custom subjects in the school
  // Hack for Stig skole
  const handleCreateAllIndividualGoals = async () => {
    const studentId = (student as UserType).id
    const schoolSubjects = $dataStore.subjects
    // This works because at this point, schoolSubjects are only custom subjects, not all subjects whatsoever
    const goalPromises = schoolSubjects.flatMap(subject =>
      Array.from({ length: individualGoalcount }, (_, i) => {
        const goal: GoalCreateType = {
          studentId,
          subjectId: subject.id,
          sortOrder: i + 1,
          masterySchemaId: $dataStore.defaultMasterySchema?.id,
          schoolId: currentSchool.id,
          isRelevant: true,
        }
        return goalsCreate({ body: goal }).then(() => {
          trackEvent('Goals', 'Create', 'type', 2)
        })
      })
    )

    await Promise.all(goalPromises)
    fetchStudentData()
  }

  $effect(() => {
    fetchStudentData()
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
        {#if individualStudentGoalsCount === 0 && currentSchool.subjectsAllowed === SUBJECTS_ALLOWED_CUSTOM}
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
          <GoalWidgets
            {student}
            masterySchema={$dataStore.defaultMasterySchema?.id}
            isIndividual={true}
            isRelevant={true}
            onRefreshRequired={() => fetchStudentData()}
            widgets={['create']}
          />
        {/if}
      </div>

      {#if subjects.length > 0}
        <ul class="list-group list-group-flush">
          {#each subjects as subject (subject.id)}
            <li class="list-group-item py-3">
              <StudentSubjectGoals
                {subject}
                {student}
                onRefreshRequired={() => fetchStudentData()}
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
