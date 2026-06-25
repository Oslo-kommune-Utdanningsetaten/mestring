<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../types/models'
  import { localStorage } from '../stores/localStorage'
  import { currentUser } from '../stores/data'
  import Beehive from './masteryBadges/Beehive.svelte'
  import Circle from './masteryBadges/Circle.svelte'
  import Triangle from './masteryBadges/Triangle.svelte'
  import Smiley from './masteryBadges/Smiley.svelte'
  import {
    MISSING_REASON_NO_OBSERVATIONS,
    MISSING_REASON_NO_GOALS,
    MASTERY_BADGE_VARIANTS,
  } from '../utils/constants'

  const {
    masteryData,
    masterySchema,
    variant,
    dataMissingReason = undefined,
  } = $props<{
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    variant?:
      | MASTERY_BADGE_VARIANTS.BEEHIVE
      | MASTERY_BADGE_VARIANTS.CIRCLE
      | MASTERY_BADGE_VARIANTS.TRIANGLE
      | MASTERY_BADGE_VARIANTS.SMILEY
    dataMissingReason?: typeof MISSING_REASON_NO_OBSERVATIONS | typeof MISSING_REASON_NO_GOALS
  }>()

  const preferredMasteryBadgeVariant = localStorage<MASTERY_BADGE_VARIANTS>(
    'preferredMasteryBadgeVariant'
  )
  const currentBadgeVariant = $derived(
    variant || $preferredMasteryBadgeVariant || MASTERY_BADGE_VARIANTS.BEEHIVE
  )
  const isMasteryValueVisible = $derived(masterySchema?.config?.isMasteryValueVisible ?? false)
  // Students should not see mastery values if the schema is configured to hide them
  const isLastValueVisible = $derived(!$currentUser.isStudent || isMasteryValueVisible)
  const isBadgeEmpty = $derived(dataMissingReason === MISSING_REASON_NO_OBSERVATIONS)
  const isBadgeVoid = $derived(dataMissingReason === MISSING_REASON_NO_GOALS)

  const mastery = $derived(masteryData?.mastery ?? 0)
  const trend = $derived(masteryData?.trend ?? 0)

  const title = $derived.by(() => {
    const isAggregated = masteryData?.goalsCount > 1 // multiple goals means aggregated data
    const lastValueTitle = isMasteryValueVisible && isAggregated ? `Siste verdi: ${mastery}` : ''
    const observationsTitle =
      isMasteryValueVisible && !isAggregated && masteryData?.observationValues?.length
        ? `Observasjoner: [${masteryData.observationValues.join(', ')}]`
        : ''
    const obsCount = masteryData?.observationValues.length ?? 0
    const aggregatedTitle = isAggregated
      ? `Aggregert: ${obsCount} observasjon${obsCount === 1 ? '' : 'er'} fordelt på ${masteryData.goalsCount} mål`
      : ''
    return [
      masterySchema?.title,
      lastValueTitle,
      observationsTitle,
      aggregatedTitle,
      'Trend: ' + trend,
    ]
      .filter(Boolean)
      .join('\n')
  })
</script>

{#if currentBadgeVariant === MASTERY_BADGE_VARIANTS.BEEHIVE}
  <Beehive
    {masteryData}
    {masterySchema}
    {title}
    {isBadgeEmpty}
    {isBadgeVoid}
    {isLastValueVisible}
  />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.CIRCLE}
  <Circle {masteryData} {masterySchema} {title} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.TRIANGLE}
  <Triangle
    {masteryData}
    {masterySchema}
    {title}
    {isBadgeEmpty}
    {isBadgeVoid}
    {isLastValueVisible}
  />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.SMILEY}
  <Smiley {masteryData} {masterySchema} {title} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else}
  <span class="border border-danger">
    Unknown badge variant {variant}
  </span>
{/if}

<style>
</style>
