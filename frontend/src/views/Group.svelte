<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import { groupsRetrieve, usersList, goalsList } from '../generated/sdk.gen'
  import type { GoalReadable, GroupReadable, UserReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { TEACHER_ROLE, STUDENT_ROLE } from '../utils/constants'
  import GoalEdit from '../components/GoalEdit.svelte'
  import { dataStore } from '../stores/data'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { groupId } = $props<{ groupId: string }>()

  let currentSchool = $derived($dataStore.currentSchool)
  let group = $state<GroupReadable | null>(null)
  let teachers = $state<UserReadable[]>([])
  let students = $state<UserReadable[]>([])
  let goals = $state<GoalReadable[]>([])
  let goalWip = $state<GoalDecorated | null>(null)
  let isLoading = $state(true)
  let error = $state<string | null>(null)

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

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      groupId: group?.id,
      sortOrder: goal.sortOrder || (goals.length ? goals.length + 1 : 1),
      masterySchemaId:
        goal.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
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

  $effect(() => {
    if (groupId && currentSchool && currentSchool.id) {
      fetchGroupData()
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
    {#if goals}
      <div class="card mb-4">
        <div class="card-header d-flex align-items-center gap-2 mb-3">
          <h3 class="mb-0">Mål</h3>
          <pkt-button
            size="small"
            skin="tertiary"
            type="button"
            variant="icon-only"
            iconName="plus-sign"
            title="Legg til nytt gruppemål"
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
            Nytt personlig mål
          </pkt-button>
        </div>
        <div class="card-body">
          {#if goals.length === 0}
            <p>Trykk pluss (+) knappen for å opprette et mål for denne gruppa</p>
          {:else}
            <ul>
              {#each goals as goal}
                <li>{goal.title}</li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    {/if}

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
  <GoalEdit {group} goal={goalWip} isGoalPersonal={false} onDone={handleGoalDone} />
</div>

<style>
</style>
