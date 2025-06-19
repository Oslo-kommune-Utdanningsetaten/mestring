<script lang="ts">
  import { groupsRetrieve, groupsMembersRetrieve } from '../generated/sdk.gen'
  import { type GroupReadable, type NestedGroupUserReadable } from '../generated/types.gen'

  const { groupId } = $props<{ groupId: string }>()

  let group = $state<GroupReadable | null>(null)
  let teachers = $state<NestedGroupUserReadable[]>([])
  let students = $state<NestedGroupUserReadable[]>([])
  let isLoading = $state(true)
  let error = $state<string | null>(null)

  const fetchGroup = async () => {
    if (!groupId) return

    try {
      isLoading = true
      error = null

      // Fetch group details
      const groupResult = await groupsRetrieve({
        path: { id: groupId },
      })
      group = groupResult.data || null

      // Fetch group members
      const membersResult = await groupsMembersRetrieve({
        path: { id: groupId },
      })
      const members: NestedGroupUserReadable[] = membersResult.data || []
      teachers = members.filter(member => member.role.name === 'teacher')
      students = members.filter(member => member.role.name === 'student')
    } catch (error) {
      console.error('Error fetching group:', error)
      error = 'Kunne ikke hente gruppeinformasjon'
    } finally {
      isLoading = false
    }
  }

  $effect(() => {
    if (groupId) {
      fetchGroup()
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
        <h1 class="mb-1">{group.displayName}</h1>
        <div class="text-muted">
          <span class="badge bg-secondary me-2">
            {group.type == 'basis' ? 'basisgruppe' : 'undervisningsgruppe'}
          </span>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="card-title mb-0">{students.length}</h3>
            <p class="card-text">Elever</p>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="card-title mb-0">{teachers.length}</h3>
            <p class="card-text">Lærere</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Teachers Section -->
    {#if teachers}
      <div class="card mb-4">
        <div class="card-header">
          <h3 class="mb-0">Lærere</h3>
        </div>
        <div class="card-body">
          <ul>
            {#each teachers as teacher}
              <li>{teacher.user.name}</li>
            {/each}
          </ul>
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
                <a href={`/students/${student.user.id}`} class="col-md-6">
                  {student.user.name}
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

<style>
</style>
