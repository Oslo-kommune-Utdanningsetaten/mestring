<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import {
    groupsRetrieve,
    usersList,
    goalsList,
    goalsDestroy,
    goalsUpdate,
    subjectsList,
  } from '../generated/sdk.gen'
  import type {
    GoalType,
    GroupType,
    UserType,
    ObservationType,
    SubjectType,
    StatusType,
  } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    TEACHER_ROLE,
    STUDENT_ROLE,
    GROUP_TYPE_BASIS,
    GROUP_TYPE_TEACHING,
  } from '../utils/constants'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import GroupSVG from '../assets/group.svg.svelte'
  import ButtonIcon from '../components/ButtonIcon.svelte'
  import ObservationEdit from '../components/ObservationEdit.svelte'
  import StatusEdit from '../components/StatusEdit.svelte'
  import GoalEdit from '../components/GoalEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import MasteryLevelBadge from '../components/MasteryLevelBadge.svelte'
  import GroupTag from '../components/GroupTag.svelte'
  import StudentsWithSubjects from '../components/StudentsWithSubjects.svelte'
  import { dataStore } from '../stores/data'
  import { goalsWithCalculatedMastery, abbreviateName } from '../utils/functions'
  import SparkbarChart from '../components/SparkbarChart.svelte'
  import Statuses from '../components/Statuses.svelte'

  const { groupId } = $props<{ groupId: string }>()

  let isLoading = $state(true)
  let goalsListElement = $state<HTMLElement | null>(null)
  let group = $state<GroupType | null>(null)
  let sortableInstance: Sortable | null = null
  let allGroups = $state<GroupType[]>([])
  let teachers = $state<UserType[]>([])
  let students = $state<UserType[]>([])
  let groupGoals = $state<GoalType[]>([])
  let goalWip = $state<GoalDecorated | null>(null)
  let goalsWithCalculatedMasteryByStudentId = $state<Record<string, GoalDecorated[]>>({})
  let observationWip = $state<ObservationType | {} | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let statusWip = $state<Partial<StatusType> | null>(null)
  let studentForObservation = $state<UserType | null>(null)
  let isObservationEditorOpen = $state<boolean>(false)
  let isStatusEditorOpen = $state<boolean>(false)
  let isGoalEditorOpen = $state<boolean>(false)
  let currentSchool = $derived($dataStore.currentSchool)
  let subjects = $state<SubjectType[]>([])
  let subject = $derived<SubjectType | null>(subjects.find(s => s.id === group?.subjectId) || null)
  let statusesKey = $state<number>(0) // key used to force re-render of Statuses component
  const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)
  const today = new Date()

  const fetchGroupData = async () => {
    try {
      isLoading = true

      // Fetch group details
      const groupResult = await groupsRetrieve({
        path: { id: groupId },
      })
      group = groupResult.data || null

      // Fetch group members, this can be optimized to a single call, then filtered by role
      const teachersResult = await usersList({
        query: { groups: groupId, school: currentSchool.id, roles: TEACHER_ROLE },
      })
      const studentsResult = await usersList({
        query: { groups: groupId, school: currentSchool.id, roles: STUDENT_ROLE },
      })

      // Fetch goals for the group
      const goalsResult = await goalsList({
        query: { group: groupId },
      })
      teachers = teachersResult.data || []
      students = studentsResult.data || []
      groupGoals = goalsResult.data || []

      // For each student, fetch their goals with calculated mastery
      await Promise.all(
        students.map(async student => {
          return goalsWithCalculatedMastery(student.id, groupGoals).then(calculatedGoals => {
            goalsWithCalculatedMasteryByStudentId[student.id] = calculatedGoals
          })
        })
      )
      // Fetch subjects for students
      const subjectsResult = await subjectsList({
        query: { school: currentSchool.id, students: students.map(s => s.id).join(',') },
      })
      subjects = subjectsResult.data || []
    } catch (error) {
      console.error('Error fetching group:', error)
    } finally {
      isLoading = false
    }
  }

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  // Get the calculated mastery for a specific student's goal
  const getDecoratedGoalFor = (studentId: string, goalId: string) => {
    const studentGoals = goalsWithCalculatedMasteryByStudentId[studentId] || []
    const goal = studentGoals.find(g => g.id === goalId)
    return goal || null
  }

  // Does any student have observations for this goal
  const isGoalInUse = (goalId: string): boolean => {
    return Object.values(goalsWithCalculatedMasteryByStudentId).some(studentGoals =>
      studentGoals.some(g => g.id === goalId && g.observations && g.observations.length > 0)
    )
  }

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      groupId: group?.id || null,
      isGoalPersonal: false,
      sortOrder: goal?.sortOrder || (groupGoals?.length ? groupGoals.length + 1 : 1),
      masterySchemaId: goal?.masterySchemaId || $dataStore.defaultMasterySchema?.id,
      isRelevant: goal?.id ? goal?.isRelevant : true,
    }
    isGoalEditorOpen = true
  }

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goalsDestroy({ path: { id: goalId } })
      await fetchGroupData()
    } catch (error) {
      console.error('Error deleting goal:', error)
    }
  }

  const handleGoalDone = async () => {
    isGoalEditorOpen = false
    await fetchGroupData()
  }

  const handleObservationDone = async () => {
    isObservationEditorOpen = false
    fetchGroupData()
  }

  const handleEditObservation = (
    goal: GoalDecorated,
    observation: ObservationType | null,
    student: UserType
  ) => {
    goalForObservation = goal
    studentForObservation = student
    if (observation) {
      // edit observation
      observationWip = observation
    } else {
      // create new observation, prefill with value from previous observation
      const studentGoal = goalsWithCalculatedMasteryByStudentId[student.id].find(
        g => g.id === goal.id
      )
      const prevousObservations = studentGoal?.observations || []
      const previousObservation = prevousObservations[prevousObservations.length - 1]
      observationWip = {
        masteryValue: previousObservation?.masteryValue || null,
        studentId: student.id,
        goalId: goal.id,
        observerId: $dataStore.currentUser.id,
      }
    }
    isObservationEditorOpen = true
  }

  const handleEditStatus = async (status: Partial<StatusType> | null, student: UserType) => {
    if (status?.id) {
      statusWip = {
        ...status,
      }
    } else {
      statusWip = {
        subjectId: subject?.id,
        studentId: student.id,
        schoolId: $dataStore.currentSchool.id,
        beginAt: sixtyDaysAgo.toISOString().split('T')[0],
        endAt: today.toISOString().split('T')[0],
      }
    }
    isStatusEditorOpen = true
  }

  const handleStatusDone = async () => {
    goalForObservation = null
    isStatusEditorOpen = false
    statusesKey++
  }

  const handleGoalOrderChange = async (event: SortableEvent) => {
    const { oldIndex, newIndex } = event
    if (oldIndex === undefined || newIndex === undefined) return

    const localGoals = [...groupGoals]
    // Remove moved goal and capture it
    const [movedGoal] = localGoals.splice(oldIndex, 1)
    // Insert moved goal at new index
    localGoals.splice(newIndex, 0, movedGoal)
    // for each goal, update its sortOrder if it has changed
    const updatePromises: Promise<any>[] = localGoals.map(async (goal, index) => {
      const newSortOrder = index + 1 // for human readability, sortOrder starts at 1
      console.log('goal', goal.title, '-->', newSortOrder)
      if (goal.sortOrder !== newSortOrder) {
        goal.sortOrder = newSortOrder
        return goalsUpdate({
          path: { id: goal.id },
          body: goal,
        })
      } else {
        return Promise.resolve() // no update needed
      }
    })
    try {
      await Promise.all(updatePromises)
      await fetchGroupData()
    } catch (error) {
      console.error('Error updating goal order:', error)
      // Refetch to restore correct state
      await fetchGroupData()
    }
  }

  $effect(() => {
    if (groupId && currentSchool && currentSchool.id) {
      fetchGroupData()
    }
  })

  $effect(() => {
    if (goalsListElement) {
      sortableInstance = new Sortable(goalsListElement, {
        animation: 150,
        handle: '.row-handle-draggable',
        onEnd: handleGoalOrderChange,
      })
    }
    return () => {
      // clean up if element unmounts
      if (!goalsListElement && sortableInstance) {
        sortableInstance.destroy()
        sortableInstance = null
      }
    }
  })
</script>

{#if isLoading}
  <div class="spinner-border text-primary" role="status">
    <span class="visually-hidden">Henter data...</span>
  </div>
{:else if !group}
  <div class="alert alert-warning">
    <h4>Fant ikke gruppen</h4>
    <p>
      Gruppe <span class="fw-bold">{groupId}</span>
      eksisterer ikke, eller du mangler tilgang.
    </p>
  </div>
{:else}
  <!-- Group Header -->
  <section>
    <div class="d-flex align-items-center gap-3 mb-3">
      <div class="group-svg" title="Gruppe">
        <GroupSVG />
      </div>
      <div>
        <h1 class="mb-2" title="Gruppe">
          {group.displayName}
        </h1>
        {#if subject}
          <h5 class="text-secondary" title={subject.grepCode}>{subject.displayName}</h5>
        {/if}
      </div>
    </div>
    <div class="d-flex align-items-center gap-2 mt-1">
      <GroupTag {group} isGroupTypeNameEnabled={true} />
      {#each teachers as teacher}
        <pkt-tag iconName="lecture" skin="yellow">
          <span>{abbreviateName(teacher.name)}</span>
        </pkt-tag>
      {/each}
    </div>
  </section>

  <!-- Group goals Section -->
  {#if currentSchool?.isGroupGoalEnabled && group.subjectId}
    <section>
      <div class="d-flex align-items-center gap-2">
        <h2>Mål</h2>
        <ButtonIcon
          options={{
            iconName: 'goal',
            title: `Legg til nytt gruppemål for ${group.displayName}`,
            classes: 'bordered',
            onClick: () => handleEditGoal(null),
          }}
        />
      </div>

      <div bind:this={goalsListElement} class="list-group mt-3">
        {#each groupGoals as goal, index (goal.id)}
          <div class="list-group-item goal-row {goal.isRelevant ? '' : 'hatched-background'}">
            <!-- Drag handle -->
            <span>
              <pkt-icon
                title="Endre rekkefølge"
                class="me-2 row-handle-draggable"
                name="drag"
                role="button"
                tabindex="0"
              ></pkt-icon>
            </span>
            <!-- Numbering -->
            <span>
              {goal.sortOrder || index + 1}
            </span>
            <!-- Goal type icon -->
            <span class="goal-type-icon"><GroupSVG /></span>
            <!-- Goal title -->
            <span>
              {$dataStore.currentSchool.isGoalTitleEnabled ? goal.title : ''}
            </span>
            <!-- Actions -->
            <span>
              {#if isGoalInUse(goal.id)}
                <pkt-icon
                  name="lock-locked"
                  size="small"
                  title="Målet er i bruk av en eller flere elever"
                ></pkt-icon>
              {:else}
                <ButtonIcon
                  options={{
                    iconName: 'trash-can',
                    title: 'Slett mål',
                    classes: 'bordered',
                    disabled: !goal.isRelevant || isGoalInUse(goal.id),
                    onClick: () => handleDeleteGoal(goal.id),
                  }}
                />
                <ButtonIcon
                  options={{
                    iconName: 'edit',
                    title: 'Rediger mål',
                    classes: 'bordered',
                    onClick: () => handleEditGoal(goal),
                  }}
                />
              {/if}
            </span>
          </div>
        {/each}
      </div>
    </section>
  {/if}

  <!-- Students Section -->
  <section>
    <h2 class="mb-3">Elever</h2>
    {#if group.type === GROUP_TYPE_BASIS}
      <StudentsWithSubjects {students} {subjects} groups={allGroups} />
    {:else if group.type === GROUP_TYPE_TEACHING && subject}
      <div
        class="teaching-grid my-3"
        aria-label="Elevliste"
        style="--columns-count: {groupGoals.length}"
      >
        <span class="item header header-row">Elev</span>
        {#each groupGoals as goal (goal.id)}
          <span class="item header header-row">
            <span class="column-header {goal.isRelevant ? '' : 'hatched-background text-muted'}">
              {goal.title || goal.sortOrder}
            </span>
          </span>
        {/each}
        {#each students as student (student.id)}
          <span class="item">
            <a href={`/students/${student.id}`}>
              {student.name}
            </a>
            {#key statusesKey}
              <Statuses {student} {subject} />
            {/key}
            <ButtonIcon
              options={{
                iconName: 'achievement',
                classes: 'bordered',
                title: 'Legg til ny status',
                onClick: () => handleEditStatus(null, student),
              }}
            />
          </span>
          {#each groupGoals as goal (goal.id)}
            {@const decoGoal = getDecoratedGoalFor(student.id, goal.id)}
            <span class="item gap-1">
              {#if decoGoal?.masteryData}
                <MasteryLevelBadge
                  masteryData={decoGoal.masteryData}
                  masterySchema={getMasterySchmemaForGoal(goal)}
                />
                <SparkbarChart
                  data={decoGoal.observations?.map((o: ObservationType) => o.masteryValue)}
                  masterySchema={getMasterySchmemaForGoal(goal)}
                />
              {:else}
                <MasteryLevelBadge isBadgeEmpty={true} />
              {/if}
              <span class="add-observation-button">
                <ButtonIcon
                  options={{
                    iconName: 'bullseye',
                    title: 'Legg til observasjon',
                    classes: 'bordered',
                    disabled: !goal.isRelevant,
                    onClick: () => handleEditObservation(goal, null, student),
                  }}
                />
              </span>
            </span>
          {/each}
        {/each}
      </div>
    {:else}
      <h5 class="alert alert-warning">ukjent gruppetype</h5>
    {/if}
  </section>
{/if}

<!-- Offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isGoalEditorOpen}
  ariaLabel="Rediger mål"
  onClosed={() => {
    goalWip = null
    fetchGroupData()
  }}
>
  {#if goalWip}
    <GoalEdit goal={goalWip} {group} isGoalPersonal={false} onDone={handleGoalDone} />
  {/if}
</Offcanvas>

<!-- Offcanvas for adding an observation -->
<Offcanvas
  bind:isOpen={isObservationEditorOpen}
  ariaLabel="Rediger observasjon"
  onClosed={() => {
    observationWip = null
    fetchGroupData()
  }}
>
  {#if observationWip}
    <ObservationEdit
      student={studentForObservation}
      observation={observationWip}
      goal={goalForObservation}
      onDone={handleObservationDone}
    />
  {/if}
</Offcanvas>

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  width="60vw"
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit status={statusWip} {subject} onDone={handleStatusDone} />
  {/if}
</Offcanvas>

<style>
  section {
    margin-bottom: 2rem;
  }

  .group-svg > :global(svg) {
    height: 7rem;
  }

  /* Teaching group grid - different from StudentsWithSubjects */
  .teaching-grid {
    display: grid;
    grid-template-columns: 3fr repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .teaching-grid .item {
    padding: 0.5rem;
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
  }

  .add-observation-button {
    display: flex;
    margin-left: auto;
  }

  .teaching-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .column-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
    padding: 0.1rem 0.1rem 0.1rem 0.3rem;
    max-width: 5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border: 1px solid var(--pkt-color-grays-gray-100);
  }

  .goal-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 6fr 2fr;
    column-gap: 5px;
    background-color: var(--bs-light);
    min-height: 3rem;
    align-items: center;
  }

  .row-handle-draggable {
    cursor: move;
    vertical-align: -8%;
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }
</style>
