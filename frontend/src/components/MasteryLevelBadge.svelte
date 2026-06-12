<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../types/models'
  import Beehive from './masteryBadges/Beehive.svelte'
  import Circle from './masteryBadges/Circle.svelte'
  import Triangle from './masteryBadges/Triangle.svelte'
  import Smiley from './masteryBadges/Smiley.svelte'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'

  const {
    masteryData,
    masterySchema,
    isLastValueVisible = true,
    variant = 'beehive',
    dataMissingReason = undefined,
  } = $props<{
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    variant?: 'beehive' | 'circle' | 'triangle' | 'smiley'
    dataMissingReason?: typeof MISSING_REASON_NO_OBSERVATIONS | typeof MISSING_REASON_NO_GOALS
  }>()

  const isBadgeEmpty = $derived(dataMissingReason === MISSING_REASON_NO_OBSERVATIONS)
  const isBadgeVoid = $derived(dataMissingReason === MISSING_REASON_NO_GOALS)
</script>

{#if variant === 'beehive'}
  <Beehive {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if variant === 'circle'}
  <Circle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if variant === 'triangle'}
  <Triangle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if variant === 'smiley'}
  <Smiley {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else}
  <span class="border border-danger">
    Unknown badge variant {variant}
  </span>
{/if}

<style>
</style>
