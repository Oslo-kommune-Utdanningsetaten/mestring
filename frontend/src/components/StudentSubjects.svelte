<script lang="ts">
  import type { ObservationType, GroupType, SubjectType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { groupsList } from '../generated/sdk.gen'
  import { fetchGoalsForSubjectAndStudent } from '../utils/functions'
  import StudentSubjectChart from './StudentSubjectChart.svelte'

  let { currentSchool, currentUser, subjects } = $derived($dataStore)
  let groups = $state<GroupType[]>([])
  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let hoveredSubjectId = $state<string | null>(null)
  let studentSubjects = $state<SubjectType[]>([])

  const fetchData = async () => {
    try {
      const groupsResult = await groupsList({
        query: { school: currentSchool.id, user: currentUser.id },
      })
      groups = (groupsResult.data || []).filter(group => group.type === 'teaching')
    } catch (error) {
      console.error(`Could not load subjects for ${currentUser.id}`, error)
      groups = []
    }
    studentSubjects = subjects.filter(subject =>
      groups.some(group => group.subjectId === subject.id)
    )

    await Promise.all(
      studentSubjects.map(async subject => {
        const goals = await fetchGoalsForSubjectAndStudent(
          subject.id,
          currentUser.id,
          currentSchool?.id!,
          currentUser.allGroups
        )
        goals.sort((a, b) => latestObservationDate(b).localeCompare(latestObservationDate(a)))
        goalsBySubjectId = { ...goalsBySubjectId, [subject.id]: goals }
      })
    )
  }

  const latestObservationDate = (goal: GoalDecorated): string => {
    if (!goal.observations?.length) return ''
    return goal.observations
      .map((o: ObservationType) => o.observedAt || o.createdAt || '')
      .sort()
      .at(-1)!
  }

  $effect(() => {
    if (currentSchool) {
      fetchData()
    }
  })
</script>

<section class="py-4">
  <h2>Mine fag</h2>

  {#if groups.length < 1}
    <div class="mt-3">🫤 Ingen fag, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4">
      <ul class="list-group list-group-flush">
        {#each groups as group (group.id)}
          {@const subject = studentSubjects.find(s => s.id === group.subjectId)}
          {#if subject}
            {@const subjectName = subject.shortName || subject.displayName || subject.grepCode}
            <li class="list-group-item">
              <h3 class="mt-3 mb-1">
                {subjectName}
              </h3>
              <hr class="border border-1 mt-0" />
              <div class="subject-card-layout py-3">
                <ul class="goals-list list-unstyled mb-0">
                  {#each goalsBySubjectId[subject.id] as goal (goal.id)}
                    <li
                      class="goal-row d-flex align-items-center justify-content-between gap-2 py-1"
                    >
                      <span>{goal.title}</span>
                      {#if goal.observations?.length}
                        <span class="badge rounded-pill bg-secondary flex-shrink-0">
                          {goal.observations.length}
                        </span>
                      {/if}
                    </li>
                  {/each}
                </ul>

                <div
                  class="chart-wrapper"
                  role="img"
                  aria-label="Mestringsoversikt for {subjectName}"
                  onmouseover={() => {
                    hoveredSubjectId = subject.id
                  }}
                  onmouseleave={() => {
                    hoveredSubjectId = null
                  }}
                  onfocus={() => {
                    hoveredSubjectId = subject.id
                  }}
                  onblur={() => {
                    hoveredSubjectId = null
                  }}
                >
                  <StudentSubjectChart
                    student={currentUser}
                    {subject}
                    isLabelEnabled={hoveredSubjectId === subject.id}
                  />
                </div>
              </div>
            </li>
          {/if}
        {/each}
      </ul>
    </div>
  {/if}
</section>

<style>
  hr {
    border-color: var(--bs-primary-rgb) !important;
    opacity: 25%;
  }

  .subject-card-layout {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }

  .goals-list {
    width: 60%;
  }

  .goal-row {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .goal-row:last-child {
    border-bottom: none;
  }

  @media (min-width: 768px) {
    .subject-card-layout {
      position: relative;
      padding-right: calc(35% + 1rem);
    }

    .goals-list {
      width: 100%;
    }

    .chart-wrapper {
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      width: 35%;
    }
  }
</style>
