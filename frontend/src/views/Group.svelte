<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import {
    groupsRetrieve,
    usersList,
    goalsList,
    goalsDestroy,
    goalsUpdate,
  } from '../generated/sdk.gen'
  import type {
    GoalType,
    GroupType,
    UserType,
    ObservationType,
    SubjectType,
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
  import ButtonMini from '../components/ButtonMini.svelte'
  import ObservationEdit from '../components/ObservationEdit.svelte'
  import GoalEdit from '../components/GoalEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import MasteryLevelBadge from '../components/MasteryLevelBadge.svelte'
  import SparklineChart from '../components/SparklineChart.svelte'
  import GroupTypeTag from '../components/GroupTypeTag.svelte'
  import StudentRow from '../components/StudentRow.svelte'
  import { dataStore } from '../stores/data'

  import { getLocalStorageItem } from '../stores/localStorage'

  import { goalsWithCalculatedMastery, fetchSubjectsForStudents } from '../utils/functions'

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
  let studentForObservation = $state<UserType | null>(null)
  let isObservationEditorOpen = $state<boolean>(false)
  let isGoalEditorOpen = $state<boolean>(false)
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let expandedGoals = $state<Record<string, boolean>>({})
  let currentSchool = $derived($dataStore.currentSchool)
  let subjects = $derived<SubjectType[]>($dataStore.subjects)
  let subject = $derived<SubjectType | null>(subjects.find(s => s.id === group?.subjectId) || null)

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

      // for each student, fetch their goals with calculated mastery
      await Promise.all(
        students.map(async student => {
          return goalsWithCalculatedMastery(student.id, groupGoals).then(calculatedGoals => {
            goalsWithCalculatedMasteryByStudentId[student.id] = calculatedGoals
          })
        })
      )
    } catch (error) {
      console.error('Error fetching group:', error)
    } finally {
      isLoading = false
    }
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
      masterySchemaId:
        goal?.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
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
        {:else}
          <h5 class="text-secondary">Ikke tilknyttet et fag</h5>
        {/if}
      </div>
    </div>
    <div class="d-flex align-items-center gap-2 mt-1">
      <GroupTypeTag {group} />
      {#each teachers as teacher}
        <pkt-tag iconName="lecture" skin="yellow">
          <span>{teacher.name}</span>
        </pkt-tag>
      {/each}
    </div>
  </section>

  <!-- Group goals Section -->
  {#if currentSchool?.isGroupGoalEnabled && group.subjectId}
    <section>
      <div class="d-flex align-items-center gap-2">
        <h2>Mål</h2>
        <ButtonMini
          options={{
            iconName: 'plus-sign',
            classes: 'mini-button bordered',
            title: `Legg til nytt gruppemål for ${group.displayName}`,
            variant: 'icon-only',
            skin: 'tertiary',
            onClick: () => handleEditGoal(null),
          }}
        >
          Nytt gruppemål
        </ButtonMini>
      </div>

      <div bind:this={goalsListElement} class="list-group mt-3">
        {#each groupGoals as goal, index (goal.id)}
          <div class="list-group-item goal-row">
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
              {isShowGoalTitleEnabled ? goal.title : '🙊'}
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
                <ButtonMini
                  options={{
                    title: 'Rediger mål',
                    iconName: 'edit',
                    skin: 'secondary',
                    variant: 'icon-only',
                    size: 'tiny',
                    classes: 'me-1',
                    onClick: () => handleEditGoal(goal),
                  }}
                />
                <ButtonMini
                  options={{
                    title: 'Slett mål',
                    iconName: 'trash-can',
                    skin: 'secondary',
                    variant: 'icon-only',
                    size: 'tiny',
                    classes: 'me-0',
                    onClick: () => handleDeleteGoal(goal.id),
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
      <div
        class="students-grid"
        aria-label="Elevliste"
        style="--columns-count: {$dataStore.subjects.length}"
      >
        <span class="item header header-row">Elev</span>
        {#each $dataStore.subjects as subject, index (subject.id)}
          <span class="item header header-row">
            <span class="subject-label-header">
              {subject.shortName}
            </span>
          </span>
        {/each}
        {#each students as student (student.id)}
          <StudentRow {student} subjects={$dataStore.subjects} groups={allGroups} />
        {/each}
      </div>
    {:else if group.type === GROUP_TYPE_TEACHING}
      <div
        class="students-grid my-3"
        aria-label="Elevliste"
        style="--columns-count: {groupGoals.length}"
      >
        <span class="item header header-row">Elev</span>
        {#each groupGoals as goal (goal.id)}
          <span class="item header header-row">
            <span class="subject-label-header">
              {goal.title || goal.sortOrder}
            </span>
          </span>
        {/each}
        {#each students as student (student.id)}
          <span class="item">
            {student.name}
          </span>
          {#each groupGoals as goal (goal.id)}
            {@const decoGoal = getDecoratedGoalFor(student.id, goal.id)}
            <span class="item">
              {#if decoGoal?.masteryData}
                <MasteryLevelBadge masteryData={decoGoal.masteryData} />
                <SparklineChart
                  data={decoGoal.observations?.map((o: ObservationType) => o.masteryValue)}
                />
              {:else}
                <MasteryLevelBadge isBadgeEmpty={true} />
              {/if}
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

<style>
  section {
    margin-bottom: 2rem;
  }

  .group-svg > :global(svg) {
    height: 7rem;
  }

  .students-grid {
    display: grid;
    grid-template-columns: 3fr repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-top: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
  }

  .students-grid :global(.item.header-row) {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .students-grid :global(.item.last-row) {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .subject-label-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
  }

  .goal-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 6fr 1fr;
    column-gap: 5px;
    background-color: var(--bs-light);
  }

  .row-handle-draggable {
    cursor: move;
    vertical-align: -8%;
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }
</style>
