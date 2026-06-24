<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../types/models'
  import { localStorage } from '../stores/localStorage'
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
    isLastValueVisible = true,
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
  const isBadgeEmpty = $derived(dataMissingReason === MISSING_REASON_NO_OBSERVATIONS)
  const isBadgeVoid = $derived(dataMissingReason === MISSING_REASON_NO_GOALS)
</script>

{#if currentBadgeVariant === MASTERY_BADGE_VARIANTS.BEEHIVE}
  <Beehive {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.CIRCLE}
  <Circle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.TRIANGLE}
  <Triangle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if currentBadgeVariant === MASTERY_BADGE_VARIANTS.SMILEY}
  <Smiley {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else}
  <span class="border border-danger">
    Unknown badge variant {variant}
  </span>
{/if}

<style>
</style>
