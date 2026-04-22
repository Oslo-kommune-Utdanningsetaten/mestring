<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { goalsRetrieve, observationsList } from '../generated/sdk.gen'
  import { getMasteryColorByValue } from '../utils/masteryHelpers'
  import AuthorInfo from './AuthorInfo.svelte'
  import UserTag from './UserTag.svelte'
  import { USER_ROLES } from '../utils/constants'

  let { currentSchool, currentUser, subjects } = $derived($dataStore)

  let observationsByMe = $state<ObservationType[]>([])
  let observationsOfMe = $state<ObservationType[]>([])
  let observations = $derived(
    [...observationsByMe, ...observationsOfMe].sort(
      (a: ObservationType, b: ObservationType) =>
        new Date(b?.observedAt ?? 0).getTime() - new Date(a?.observedAt ?? 0).getTime()
    )
  )
  let cachedGoals = $state<Record<string, GoalType>>({})

  // TODO: Fetch both observered by me and where I'm as student (possibly merge, if same). Then render in two different lists ''

  const fetchObservations = async () => {
    try {
      const [obmResult, oomResult] = await Promise.all([
        observationsList({
          query: { observer: currentUser?.id, school: currentSchool?.id },
        }),
        observationsList({
          query: { student: currentUser?.id, school: currentSchool?.id },
        }),
      ])
      observationsByMe = obmResult.data || []
      observationsOfMe = oomResult.data || []
    } catch (error) {
      console.error('Error fetching observations:', error)
    }
  }

  const lookUpGoal = async (goalId: string) => {
    try {
      const result = await goalsRetrieve({ path: { id: goalId } })
      if (result.data) {
        cachedGoals[goalId] = result.data
        cachedGoals = { ...cachedGoals } // Trigger reactivity
      }
    } catch (error) {
      console.error('Error fetching goal:', error)
    }
  }

  const getSubjectName = (subjectId: any) => {
    return subjects.find(s => s.id === subjectId)?.displayName || 'Ukjent fag'
  }

  const getMasteryColor = (observation: ObservationType): string | null => {
    const goal = cachedGoals[observation.goalId]
    if (!goal || observation.masteryValue == null) return null
    const schema = $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
    const levels = schema?.config?.levels
    if (!levels?.length) return null
    return getMasteryColorByValue(observation.masteryValue, levels)
  }

  $effect(() => {
    fetchObservations()
  })
</script>

<section class="py-4">
  <h2>Observasjoner</h2>

  {#if observations.length < 1}
    <div class="mt-3">🫤 Her var det lite, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4">
      {#each observations as observation, i}
        <div class="observation-row" class:border-top={i > 0}>
          <div class="obs-header">
            <UserTag userId={observation.studentId} role={USER_ROLES.STUDENT} />
            <div class="obs-goal">
              <div class="obs-goal-line">
                {#if cachedGoals[observation.goalId]}
                  <span class="obs-goal-title">{cachedGoals[observation.goalId].title}</span>
                {:else}
                  {void lookUpGoal(observation.goalId)}
                  <span
                    class="spinner-border spinner-border-sm"
                    role="status"
                    aria-hidden="true"
                  ></span>
                {/if}
                <span class="obs-subject">{getSubjectName(observation?.subjectId)}</span>
              </div>
              <div class="obs-meta">
                <AuthorInfo item={observation} />
              </div>
            </div>
          </div>
          <div
            class="mastery-panel"
            style={getMasteryColor(observation)
              ? `--mastery-color: ${getMasteryColor(observation)}`
              : undefined}
          >
            {#if observation.masteryDescription || observation.feedforward}
              {#if observation.masteryValue != null}
                <div class="mastery-badge">{observation.masteryValue}</div>
              {/if}
              {#if observation.masteryDescription}
                <p class="mastery-desc">{observation.masteryDescription}</p>
              {/if}
              {#if observation.feedforward}
                <div class="mastery-ff">
                  <span class="ff-icon">↗</span>
                  {observation.feedforward}
                </div>
              {/if}
            {:else if observation.masteryValue != null}
              <div class="mastery-solo">
                <span class="mastery-solo-value">{observation.masteryValue}</span>
                <span class="mastery-solo-label">mestring</span>
              </div>
            {:else}
              <span class="mastery-empty">–</span>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  .observation-row {
    padding: 0.65rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
  }

  /* ── Left side: header ── */
  .obs-header {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .obs-goal {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .obs-goal-line {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .obs-goal-title {
    font-weight: 600;
    font-size: 0.975rem;
    line-height: 1.3;
  }

  .obs-subject {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #666;
    background: #ebebeb;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* ── Meta row ── */
  .obs-meta {
    font-size: 0.72rem;
    color: #999;
  }

  /* ── Mastery panel ───────────────────────────────── */
  .mastery-panel {
    flex-shrink: 0;
    width: 40%;
    border-radius: 12px;
    padding: 0.75rem;
    position: relative;
    font-size: 0.825rem;
    line-height: 1.45;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-self: stretch;
    min-height: 3.5rem;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }

  /* Color themes — driven by --mastery-color custom property */
  .mastery-panel {
    --mastery-color: #888;
    background: color-mix(in srgb, var(--mastery-color) 12%, white);
    color: color-mix(in srgb, var(--mastery-color) 80%, black);
  }

  /* ── Value badge (corner) ── */
  .mastery-badge {
    position: absolute;
    top: -0.6rem;
    right: -0.6rem;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    color: #fff;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    background: var(--mastery-color);
  }

  /* ── Rich text content ── */
  .mastery-desc {
    margin: 0;
    font-weight: 500;
  }

  .mastery-ff {
    display: flex;
    gap: 0.3rem;
    font-style: italic;
    opacity: 0.85;
    border-top: 1px solid currentColor;
    padding-top: 0.4rem;
    margin-top: auto;
  }

  .ff-icon {
    flex-shrink: 0;
    font-style: normal;
    font-weight: 700;
  }

  /* ── Solo value display ── */
  .mastery-solo {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
  }

  .mastery-solo-value {
    font-size: 2.75rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.02em;
  }

  .mastery-solo-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.65;
    font-weight: 600;
  }

  .mastery-empty {
    opacity: 0.35;
    margin: auto;
  }
</style>
