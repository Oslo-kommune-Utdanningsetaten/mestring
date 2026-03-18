<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { GoalType } from '../../generated/types.gen'
  import { goalsList, usersList } from '../../generated/sdk.gen'
  import { formatDateTime } from '../../utils/functions'
  import { addAlert } from '../../stores/alerts'
  import { dataStore } from '../../stores/data'
  import Link from '../../components/Link.svelte'

  const currentSchool = $derived($dataStore.currentSchool)
  let goals = $state<GoalType[]>([])
  let creatorsById = $state<Record<string, string>>({})

  // Sort state
  type SortKey = 'type' | 'title' | 'createdBy' | 'createdAt' | 'belongsTo'
  let sortBy = $state<SortKey>('createdAt')
  let sortDirection = $state<'asc' | 'desc'>('desc')

  const fetchGoals = async () => {
    try {
      const result = await goalsList({ query: { school: currentSchool?.id } })

      goals = result.data || []
      fetchGoalCreators()
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av mål',
      })
      goals = []
    }
  }

  const fetchGoalCreators = async () => {
    if (goals.length === 0) return
    try {
      const creatorIds = Array.from(new Set(goals.map(goal => goal.createdById).filter(Boolean)))
      if (creatorIds.length === 0) return

      const result = await usersList({
        query: { ids: creatorIds.join(','), school: currentSchool.id },
      })
      const users = result.data || []
      creatorsById = users.reduce(
        (acc, user) => {
          acc[user.id] = user.name
          return acc
        },
        {} as Record<string, string>
      )
    } catch (error) {
      addAlert({
        type: 'danger',
        message: 'Feil ved henting av målskaper-informasjon',
      })
    }
  }

  // Sorted goals list
  let sortedGoals = $derived.by(() => {
    const sorted = [...goals]
    sorted.sort((a, b) => {
      let comparison: number
      if (sortBy === 'type') {
        // Sort by isIndividual: individual (true) comes before group (false)
        comparison = Number(b.isIndividual) - Number(a.isIndividual)
      } else if (sortBy === 'title') {
        const titleA = a.title || `${a.sortOrder ?? ''}`
        const titleB = b.title || `${b.sortOrder ?? ''}`
        comparison = titleA.localeCompare(titleB, 'no')
      } else if (sortBy === 'belongsTo') {
        const idA = a.studentId || a.groupId
        const idB = b.studentId || b.groupId
        comparison = (idA as string).localeCompare(idB as string, 'no')
      } else if (sortBy === 'createdBy') {
        comparison = (a.createdById || '').localeCompare(b.createdById || '', 'no')
      } else if (sortBy === 'createdAt') {
        const timeA = a.createdAt || '0'
        const timeB = b.createdAt || '0'
        comparison = new Date(timeA).getTime() - new Date(timeB).getTime()
      } else {
        comparison = 0
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })
    return sorted
  })

  const handleHeaderClick = (key: SortKey) => {
    if (sortBy === key) {
      // Toggle direction
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      // New sort key
      sortBy = key
      sortDirection = 'asc'
    }
  }

  const getSortIndicator = (key: SortKey): string => {
    if (sortBy !== key) return ''
    return sortDirection === 'asc' ? '▲' : '▼'
  }

  const getBelongsToLink = (goal: GoalType): string => {
    if (goal.isIndividual) {
      return `/students/${goal.studentId}`
    } else {
      return `/groups/${goal.groupId}`
    }
  }

  $effect(() => {
    fetchGoals()
  })
</script>

<section class="py-3">
  <h2>Alle mål ved skolen</h2>

  {#if goals.length > 0}
    <!-- Header -->
    <div class="goals-grid mt-4">
      <span class="header">
        <button
          class="sort-button"
          onclick={() => handleHeaderClick('type')}
          title="Sorter etter type"
        >
          Type{getSortIndicator('type')}
        </button>
      </span>
      <span class="header">
        <button
          class="sort-button"
          onclick={() => handleHeaderClick('title')}
          title="Sorter etter tittel"
        >
          {currentSchool?.isGoalTitleEnabled ? 'Tittel' : 'Sortering'}
          {getSortIndicator('title')}
        </button>
      </span>
      <span class="header">
        <button
          class="sort-button"
          onclick={() => handleHeaderClick('belongsTo')}
          title="Sorter etter eierskap"
        >
          Tilhører{getSortIndicator('belongsTo')}
        </button>
      </span>
      <span class="header">
        <button
          class="sort-button"
          onclick={() => handleHeaderClick('createdBy')}
          title="Sorter etter opprettet av"
        >
          Opprettet av{getSortIndicator('createdBy')}
        </button>
      </span>
      <span class="header">
        <button
          class="sort-button"
          onclick={() => handleHeaderClick('createdAt')}
          title="Sorter etter opprettelsesdato"
        >
          Opprettet tid{getSortIndicator('createdAt')}
        </button>
      </span>

      <!-- Rows -->
      {#each sortedGoals as goal}
        <div>
          {#if goal.isIndividual}
            <pkt-icon name="person" size="20" aria-label="Individuelt mål"></pkt-icon>
          {:else}
            <pkt-icon name="group" size="20" aria-label="Gruppemål"></pkt-icon>
          {/if}
        </div>
        <div>
          {goal.title || goal.sortOrder}
        </div>
        <div>
          <Link to={getBelongsToLink(goal)}>
            {goal.isIndividual ? 'Elev' : 'Gruppe'}
          </Link>
        </div>
        <div>
          <Link to="/admin/users/{goal.createdById}">
            {creatorsById[goal.createdById] || goal.createdById}
          </Link>
        </div>
        <div>{formatDateTime(goal.createdAt)}</div>
      {/each}
    </div>
  {:else}
    <div class="alert alert-info mt-4">Ingen mål funnet</div>
  {/if}
</section>

<style>
  .goals-grid {
    display: grid;
    grid-template-columns: 1fr auto 2fr 4fr 4fr;
  }

  .header {
    background-color: var(--pkt-color-brand-neutrals-100);
    padding: 0.5rem;
  }

  .sort-button {
    cursor: pointer;
    border: 1px solid var(--pkt-color-grays-gray-100);
    background-color: var(--pkt-color-surface-strong-light-green);
    font-weight: 800;
    padding: 0.5rem;
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  .sort-button:hover {
    background-color: var(--bs-gray-300);
  }

  /* Target all cells in odd data rows (row 1, 3, 5...) */
  .goals-grid > div:nth-child(10n + 1),
  .goals-grid > div:nth-child(10n + 2),
  .goals-grid > div:nth-child(10n + 3),
  .goals-grid > div:nth-child(10n + 4),
  .goals-grid > div:nth-child(10n + 5) {
    background-color: var(--pkt-sand-10, #fafaf8);
    padding: 0.5rem;
  }

  /* Add padding to all data cells for consistency */
  .goals-grid > div:not(.sort-button) {
    padding: 0.5rem 0.5rem 0.5rem 1rem;
  }
</style>
