<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import {
    groupsRetrieve,
    usersList,
    goalsList,
    goalsUpdate,
    goalsDestroy,
    groupsList,
  } from '../generated/sdk.gen'
  import type {
    GoalReadable,
    GroupReadable,
    UserReadable,
    ObservationReadable,
  } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { TEACHER_ROLE, STUDENT_ROLE } from '../utils/constants'
  import GoalEdit from '../components/GoalEdit.svelte'
  import GroupSVG from '../assets/group.svg.svelte'
  import ButtonMini from '../components/ButtonMini.svelte'
  import ObservationEdit from '../components/ObservationEdit.svelte'
  import Offcanvas from '../components/Offcanvas.svelte'
  import MasteryLevelBadge from '../components/MasteryLevelBadge.svelte'
  import SparklineChart from '../components/SparklineChart.svelte'
  import GroupTypeTag from '../components/GroupTypeTag.svelte'
  import StudentRow from '../components/StudentRow.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { dataStore } from '../stores/data'
  import { getLocalStorageItem } from '../stores/localStorage'
  import { goalsWithCalculatedMastery } from '../utils/functions'

  const { groupId } = $props<{ groupId: string }>()

  let currentSchool = $derived($dataStore.currentSchool)
  let sortableInstance: Sortable | null = null
  let group = $state<GroupReadable | null>(null)
  let allGroups = $state<GroupReadable[]>([])
  let teachers = $state<UserReadable[]>([])
  let students = $state<UserReadable[]>([])
  let goals = $state<GoalReadable[]>([])
  let goalWip = $state<GoalDecorated | null>(null)
  let isLoading = $state(true)
  let error = $state<string | null>(null)
  let goalsListElement = $state<HTMLElement | null>(null)
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let expandedGoals = $state<Record<string, boolean>>({})
  let goalsWithCalculatedMasteryByStudentId = $state<Record<string, GoalDecorated[]>>({})
  let isGoalInUse = $derived<Record<string, boolean>>({}) // keyed by goalId, if true, goal has at least one observation
  let observationWip = $state<ObservationReadable | {} | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let studentForObservation = $state<UserReadable | null>(null)
  let isGoalEditorOpen = $state<boolean>(false)
  let isObservationEditorOpen = $state<boolean>(false)
  let studentsGridElement = $state<HTMLElement | null>(null)

  const fetchGroupData = async () => {
    if (!groupId) return

    try {
      isLoading = true
      error = null

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
      goals = goalsResult.data || []

      // for each student, fetch their goals with calculated mastery
      const studentPromises = students.map(async student => {
        return goalsWithCalculatedMastery(student.id, goals).then(calculatedGoals => {
          goalsWithCalculatedMasteryByStudentId[student.id] = calculatedGoals
        })
      })
      await Promise.all(studentPromises)

      // Determine if goals are in use (have observations) by any student in the group
      goals.forEach(goal => {
        isGoalInUse[goal.id] = students.some(student => {
          const studentGoals = goalsWithCalculatedMasteryByStudentId[student.id] || []
          return studentGoals.some(
            studentGoal => studentGoal.id === goal.id && studentGoal.observations?.length > 0
          )
        })
      })
      await fetchAllGroups()
    } catch (error) {
      console.error('Error fetching group:', error)
    } finally {
      isLoading = false
    }
  }

  const fetchAllGroups = async () => {
    if (!currentSchool) return
    try {
      const result = await groupsList({
        query: {
          school: currentSchool?.id,
          isEnabled: true,
        },
      })
      allGroups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      allGroups = []
    } finally {
    }
  }

  const toggleGoalExpansion = (goalId: string) => {
    expandedGoals[goalId] = !expandedGoals[goalId]
  }

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      groupId: group?.id || null,
      isGoalPersonal: false,
      sortOrder: goal?.sortOrder || (goals?.length ? goals.length + 1 : 1),
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
    observation: ObservationReadable | null,
    student: UserReadable
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

    const localGoals = [...goals]
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

  // Effect to apply last-row class to the last row of grid items
  $effect(() => {
    if (studentsGridElement && students.length > 0 && $dataStore.subjects.length > 0) {
      // Remove existing last-row classes
      const allItems = studentsGridElement.querySelectorAll('.item')
      allItems.forEach(item => item.classList.remove('last-row'))

      // Calculate how many items are in the last row
      const totalColumns = $dataStore.subjects.length + 1 // +1 for student name column
      const totalItems = allItems.length
      const itemsInLastRow = totalColumns

      // Apply last-row class to the last row items
      for (let i = totalItems - itemsInLastRow; i < totalItems; i++) {
        if (allItems[i]) {
          allItems[i].classList.add('last-row')
        }
      }
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

<section class="py-3">
  {#if isLoading}
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
  {:else if group}
    <!-- Group Header -->
    <div class="">
      <h1>{group.displayName}</h1>

      <div class="d-flex align-items-center gap-2">
        <GroupTypeTag {group} />
        {#each teachers as teacher}
          <pkt-tag iconName="lecture" skin="yellow">
            <span>{teacher.name}</span>
          </pkt-tag>
        {/each}
      </div>
    </div>

    <!-- Goals Section -->
    {#if currentSchool?.isGroupGoalEnabled}
      <div class="my-4">
        <div class="d-flex align-items-center gap-2 mb-3">
          <h2 class="mb-0">Mål</h2>
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
        <div>
          {#if goals.length === 0}
            <div class="alert alert-info">
              Ingen mål for denne gruppa. Trykk pluss (+) for å opprette mål for alle elever i
              gruppa.
            </div>
          {:else}
            <div bind:this={goalsListElement} class="list-group">
              {#each goals as goal, index (goal.id)}
                <div
                  class="list-group-item goal-item {expandedGoals[goal.id]
                    ? 'shadow border-2 z-1'
                    : ''}"
                >
                  <div class="goal-primary-row">
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
                    <!-- Expand goal info -->
                    <ButtonMini
                      options={{
                        iconName: `chevron-thin-${expandedGoals[goal.id] ? 'up' : 'down'}`,
                        classes: 'mini-button rounded justify-end',
                        title: `${expandedGoals[goal.id] ? 'Skjul' : 'Vis'} observasjoner`,
                        onClick: () => toggleGoalExpansion(goal.id),
                      }}
                    />
                  </div>

                  {#if expandedGoals[goal.id]}
                    {#if !isGoalInUse[goal.id]}
                      <div class="my-3">
                        <p>
                          Ingen observasjoner for dette målet. Trykk pluss (+) for å opprette en
                          observasjon.
                        </p>

                        <ButtonMini
                          options={{
                            iconName: 'edit',
                            classes: 'my-2 me-2',
                            title: 'Rediger personlig mål',
                            onClick: () => handleEditGoal(goal),
                            variant: 'icon-left',
                            skin: 'primary',
                          }}
                        >
                          Rediger personlig mål
                        </ButtonMini>

                        <ButtonMini
                          options={{
                            iconName: 'trash-can',
                            classes: 'my-2',
                            title: 'Slett personlig mål',
                            onClick: () => handleDeleteGoal(goal.id),
                            variant: 'icon-left',
                            skin: 'primary',
                          }}
                        >
                          Slett mål
                        </ButtonMini>
                      </div>
                    {/if}
                    <div class="goal-secondary-row">
                      {#each students as student (student.id)}
                        <div class="student-observations-in-goal mb-2 align-items-center">
                          <span>
                            {student.name}
                          </span>

                          <!-- Stats widgets -->
                          <span class="d-flex gap-2 align-items-center">
                            <MasteryLevelBadge
                              masteryData={goalsWithCalculatedMasteryByStudentId[student.id].find(
                                g => g.id === goal.id
                              ).masteryData}
                            />
                            <SparklineChart
                              data={goalsWithCalculatedMasteryByStudentId[student.id]
                                .find(g => g.id === goal.id)
                                ?.observations?.map((o: ObservationReadable) => o.masteryValue)}
                            />
                          </span>
                          <!-- New observation button -->
                          <ButtonMini
                            options={{
                              iconName: 'plus-sign',
                              classes: 'mini-button bordered',
                              title: 'Ny observasjon',
                              onClick: () => handleEditObservation(goal, null, student),
                            }}
                          />
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Students Section -->
    {#if students}
      <div class="my-4">
        <h2 class="mb-3">Elever</h2>
        <div
          bind:this={studentsGridElement}
          class="students-grid"
          aria-label="Elevliste"
          style="--subject-count: {$dataStore.subjects.length}"
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
      </div>
    {/if}
  {:else}
    <div class="alert alert-warning">
      <h4>Fant ikke gruppen</h4>
      <p>
        Gruppe <span class="fw-bold">{groupId}</span>
        eksisterer ikke, eller du mangler tilgang.
      </p>
    </div>
  {/if}
</section>

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
  .student-observations-in-goal {
    border-bottom: 1px solid rgb(from var(--bs-secondary) r g b / 25%);
    display: grid;
    grid-template-columns: 8fr 3fr 1fr;
    column-gap: 5px;
  }

  .goal-item {
    background-color: var(--bs-light);
    line-height: normal;
  }

  .goal-primary-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 15fr 1fr;
    column-gap: 5px;
  }

  .goal-secondary-row {
    margin: 10px 0 0 6px;
    padding-left: 30px;
    border-left: 3px solid rgb(from var(--bs-secondary) r g b / 25%);
  }

  .row-handle-draggable {
    cursor: move;
    vertical-align: -8%;
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }

  .students-grid {
    display: grid;
    grid-template-columns: 2fr repeat(var(--subject-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-top: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .students-grid :global(.item.header-row) {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .students-grid :global(.item.last-row) {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .students-grid :global(.item.header:first-child),
  .students-grid :global(.item.student-name) {
    justify-content: flex-start;
  }

  .subject-label-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
  }
</style>
