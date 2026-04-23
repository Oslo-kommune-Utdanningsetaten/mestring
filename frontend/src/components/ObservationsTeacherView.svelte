<script lang="ts">
  import type { ObservationType, GoalType, UserType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { goalsRetrieve, observationsList } from '../generated/sdk.gen'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'
  import AuthorInfo from './AuthorInfo.svelte'
  import UserTag from './UserTag.svelte'
  import SubjectTag from './SubjectTag.svelte'
  import Link from './Link.svelte'
  import { USER_ROLES } from '../utils/constants'
  import { isNumber } from '../utils/functions'

  let { currentSchool, currentUser, subjects } = $derived($dataStore)
  const limit = 10
  let observations = $state<ObservationType[]>([])
  let cachedGoals = $state<Record<string, GoalType>>({})

  const fetchObservations = async () => {
    try {
      const result = await observationsList({
        query: { observer: currentUser?.id, school: currentSchool?.id, limit },
      })
      observations = (result.data || []).sort(
        (a: ObservationType, b: ObservationType) =>
          new Date(b?.observedAt ?? 0).getTime() - new Date(a?.observedAt ?? 0).getTime()
      )
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

  const getMasteryLevelColor = (observation: ObservationType): string | null => {
    const goal = cachedGoals[observation.goalId]
    const schema = $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
    const levels = schema?.config?.levels
    if (!levels?.length) return null
    return getMasteryLevelColorByValue(observation.masteryValue as number, levels)
  }

  const getMasteryLevelTitle = (observation: ObservationType): string | null => {
    const goal = cachedGoals[observation.goalId]
    const schema = $dataStore.masterySchemas.find(ms => ms.id === goal?.masterySchemaId)
    const levels = schema?.config?.levels
    if (!levels?.length) return null
    return getMasteryTitleByValue(observation.masteryValue as number, levels)
  }

  $effect(() => {
    fetchObservations()
  })
</script>

<section class="py-4">
  <h2>Siste {limit > observations.length ? '' : limit} observasjoner</h2>

  {#if observations.length < 1}
    <div class="mt-3">🫤 Her var det lite, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4">
      {#each observations as observation, i}
        <div class="observation-row" class:border-top={i > 0}>
          <div class="observation-meta-panel">
            <UserTag
              userId={observation.studentId}
              role={USER_ROLES.STUDENT}
              href="/students/{observation.studentId}"
            />
            {#if cachedGoals[observation.goalId]}
              <span class="observation-goal">
                <Link to={`/students/${observation.studentId}?expanded=${observation.goalId}`}>
                  {cachedGoals[observation.goalId].title ||
                    cachedGoals[observation.goalId].sortOrder}
                </Link>
              </span>
            {:else}
              {void lookUpGoal(observation.goalId)}
              <span
                class="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
            {/if}
            <SubjectTag subjectId={observation.subjectId} />
            <div class="observation-author">
              <AuthorInfo item={observation} />
            </div>
          </div>
          <div
            class="mastery-panel"
            style={getMasteryLevelColor(observation)
              ? `--mastery-color: ${getMasteryLevelColor(observation)}`
              : undefined}
          >
            {#if observation.masteryDescription || observation.feedforward}
              {#if observation.masteryDescription}
                <span class="mastery-text">
                  <span class="mastery-icon">←</span>
                  {observation.masteryDescription}
                </span>
              {/if}
              {#if observation.masteryDescription && observation.feedforward}
                <hr class="mastery-divider" />
              {/if}
              {#if observation.feedforward}
                <div class="mastery-text">
                  <span class="mastery-icon">→</span>
                  {observation.feedforward}
                </div>
              {/if}
              {#if isNumber(observation.masteryValue)}
                <span class="mastery-value-corner">
                  <span class="mastery-level-title">
                    {getMasteryLevelTitle(observation)} ({observation.masteryValue})
                  </span>
                </span>
              {/if}
            {:else if isNumber(observation.masteryValue)}
              <div class="mastery-value-only">
                <span class="mastery-value-only">{observation.masteryValue}</span>
                <span class="mastery-level-title">{getMasteryLevelTitle(observation)}</span>
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
    padding: 1rem;
    display: flex;
    gap: 1.25rem;
  }

  .observation-meta-panel {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .observation-goal {
    font-weight: 600;
    font-size: 1rem;
    line-height: 1.3;
  }

  .observation-author {
    font-size: 0.8rem;
    color: #999;
  }

  .mastery-panel {
    position: relative;
    flex-shrink: 0;
    width: 40%;
    border-radius: 4px;
    padding: 1.5rem 0.75rem;
    line-height: 1.45;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.5rem;
    min-height: 3.5rem;
    /* Colors are set by --mastery-color custom property */
    --mastery-color: #888;
    background: color-mix(in srgb, var(--mastery-color) 12%, white);
    color: color-mix(in srgb, var(--mastery-color) 80%, black);
  }

  .mastery-value-corner {
    position: absolute;
    top: -0.6rem;
    right: -0.6rem;
    height: 2rem;
    display: flex;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    color: #fff;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    background: var(--mastery-color);
    opacity: 0.25;
    transition: opacity 0.8s ease;
  }

  .mastery-value-corner:hover {
    transition: opacity 0.3s ease;
    opacity: 0.9;
  }

  .mastery-text {
    display: flex;
    font-weight: 500;
    gap: 0.5rem;
    font-style: italic;
    opacity: 0.85;
    text-wrap: break-word;
    overflow-wrap: break-word;
  }

  .mastery-divider {
    opacity: 0.5;
    border-top: 1px solid currentColor;
    margin: 0.5rem;
  }

  .mastery-icon {
    flex-shrink: 0;
    font-style: normal;
    font-weight: 700;
  }

  .mastery-value-only {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
  }

  .mastery-value-only {
    font-size: 2.75rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.02em;
  }

  .mastery-level-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.85;
    font-weight: 600;
  }

  .mastery-empty {
    opacity: 0.35;
    margin: auto;
  }
</style>
