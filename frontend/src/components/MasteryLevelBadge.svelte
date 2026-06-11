<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../types/models'
  import Beehive from './masteryBadges/Beehive.svelte'
  import Circle from './masteryBadges/Circle.svelte'
  import Triangle from './masteryBadges/Triangle.svelte'

  const {
    masteryData,
    masterySchema,
    isBadgeEmpty = false,
    isBadgeVoid = false,
    isLastValueVisible = true,
    variant = 'beehive',
  } = $props<{
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    isBadgeEmpty?: boolean
    isBadgeVoid?: boolean
    variant?: 'beehive' | 'circle' | 'triangle'
  }>()
</script>

{#if variant === 'beehive'}
  <Beehive {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if variant === 'circle'}
  <Circle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else if variant === 'triangle'}
  <Triangle {masteryData} {masterySchema} {isBadgeEmpty} {isBadgeVoid} {isLastValueVisible} />
{:else}
  <span class="border border-danger">
    Unknown badge variant {variant}
  </span>
{/if}

<style>
</style>
