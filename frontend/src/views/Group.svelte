<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import {
    groupsRetrieve,
    usersList,
    goalsList,
    goalsUpdate,
    goalsDestroy,
  } from '../generated/sdk.gen'
  import type { GoalReadable, GroupReadable, UserReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { TEACHER_ROLE, STUDENT_ROLE } from '../utils/constants'
  import GoalEdit from '../components/GoalEdit.svelte'
  import GroupSVG from '../assets/group.svg.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { dataStore } from '../stores/data'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { groupId } = $props<{ groupId: string }>()

  let currentSchool = $derived($dataStore.currentSchool)
  let sortableInstance: Sortable | null = null
  let group = $state<GroupReadable | null>(null)
  let teachers = $state<UserReadable[]>([])
  let students = $state<UserReadable[]>([])
  let goals = $state<GoalReadable[]>([])
  let goalWip = $state<GoalDecorated | null>(null)
  let isLoading = $state(true)
  let error = $state<string | null>(null)
  let goalsListElement = $state<HTMLElement | null>(null)
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 5 : 2)
  let expandedGoals = $state<Record<string, boolean>>({})

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
      const goalsResult = await goalsList({
        query: { group: groupId },
      })
      teachers = teachersResult.data || []
      students = studentsResult.data || []
      goals = goalsResult.data || []
    } catch (error) {
      console.error('Error fetching group:', error)
      error = 'Kunne ikke hente gruppeinformasjon'
    } finally {
      isLoading = false
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
    handleCloseEditGoal()
    await fetchGroupData()
  }

  const handleCloseEditGoal = () => {
    goalWip = null
  }

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (goalWip) {
        handleCloseEditGoal()
      }
    }
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

  $effect(() => {
    if (goalsListElement) {
      sortableInstance = new Sortable(goalsListElement, {
        animation: 150,
        handle: '.row-handle',
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
  {:else if error}
    <div class="alert alert-danger">
      <h4>Noe gikk galt</h4>
      <p>{error}</p>
    </div>
  {:else if group}
    <!-- Group Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1>{group.displayName}</h1>

        <div>
          <pkt-tag iconName="two-people-dancing" skin="blue" class="me-1">
            <span>{group.type == 'basis' ? 'Basisgruppe' : 'Undervisningsgruppe'}</span>
          </pkt-tag>
          {#each teachers as teacher}
            <pkt-tag iconName="lecture" skin="green" class="me-2">
              <span>{teacher.name}</span>
            </pkt-tag>
          {/each}
        </div>
      </div>
    </div>

    <!-- Goals Section -->
    <div class="mb-4">
      <div class="d-flex align-items-center gap-2 mb-3">
        <h3 class="mb-0">Mål</h3>
        <pkt-button
          size="small"
          skin="tertiary"
          type="button"
          variant="icon-only"
          iconName="plus-sign"
          title="Legg til nytt gruppemål for {group.displayName}"
          class="mini-button bordered"
          onclick={() => handleEditGoal(null)}
          onkeydown={(e: any) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              handleEditGoal(null)
            }
          }}
          role="button"
          tabindex="0"
        >
          Nytt gruppemål
        </pkt-button>
      </div>
      <div>
        {#if goals.length === 0}
          <div class="alert alert-info">
            Ingen mål for denne gruppa. Trykk pluss (+) for å opprette mål for alle elever i gruppa.
          </div>
        {:else}
          <div bind:this={goalsListElement} class="list-group">
            {#each goals as goal, index (goal.id)}
              <div class="list-group-item goal-list-item">
                <div class="row d-flex align-items-center">
                  <span class="col-1">
                    <pkt-icon
                      title="Endre rekkefølge"
                      class="me-2 row-handle"
                      name="drag"
                      role="button"
                      tabindex="0"
                    ></pkt-icon>
                  </span>
                  <span class="col-1">
                    {goal.sortOrder || index + 1}
                  </span>
                  <span class="col-1"><GroupSVG /></span>
                  <span class="col-md-8">
                    {isShowGoalTitleEnabled ? goal.title : '🙊'}
                  </span>
                  <span class="col-1 d-flex justify-content-end pe-4">
                    <pkt-button
                      size="small"
                      skin="tertiary"
                      type="button"
                      variant="icon-only"
                      iconName="chevron-thin-{expandedGoals[goal.id] ? 'up' : 'down'}"
                      class="mini-button col-1 rounded"
                      title="{expandedGoals[goal.id] ? 'Skjul' : 'Vis'} observasjoner"
                      onclick={() => toggleGoalExpansion(goal.id)}
                      onkeydown={(e: any) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          toggleGoalExpansion(goal.id)
                        }
                      }}
                      role="button"
                      tabindex="0"
                    ></pkt-button>
                  </span>
                </div>

                {#if expandedGoals[goal.id]}
                  <div class="alert alert-info my-3">
                    <p>Ingen observasjoner for dette målet</p>

                    <pkt-button
                      size="small"
                      skin="primary"
                      variant="icon-left"
                      iconName="edit"
                      class="my-2 me-2"
                      title="Rediger dette gruppemålet"
                      onclick={() => handleEditGoal(goal)}
                      onkeydown={(e: any) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          handleEditGoal(goal)
                        }
                      }}
                      role="button"
                      tabindex="0"
                    >
                      Rediger mål
                    </pkt-button>

                    <pkt-button
                      size="small"
                      skin="primary"
                      variant="icon-left"
                      iconName="trash-can"
                      class="my-2"
                      title="Slett dette gruppemålet"
                      onclick={() => handleDeleteGoal(goal.id)}
                      onkeydown={(e: any) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          handleDeleteGoal(goal.id)
                        }
                      }}
                      role="button"
                      tabindex="0"
                    >
                      Slett mål
                    </pkt-button>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- Students Section -->
    {#if students}
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3 class="mb-0">Elever</h3>
        </div>
        <div class="card-body mb-0">
          <ul>
            {#each students as student}
              <li>
                <a href={`/students/${student.id}`} class="col-md-6">
                  {student.name}
                </a>
              </li>
            {/each}
          </ul>
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

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas" class:visible={!!goalWip}>
  <GoalEdit goal={goalWip} {group} isGoalPersonal={false} onDone={handleGoalDone} />
</div>

<style>
  div.observation-item > span {
    font-family: 'Courier New', Courier, monospace !important;
  }

  h3 {
    font-size: 1.5rem;
  }

  .goal-list-item {
    background-color: var(--bs-light);
    row-gap: 0.5rem;
  }

  .row-handle {
    cursor: move;
    vertical-align: -8%;
  }
</style>
