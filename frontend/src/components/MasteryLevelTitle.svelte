<script lang="ts">
  import type { ObservationType } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'
  import { isNumber, getContrastFriendlyTextColor } from '../utils/functions'

  const { observation, masterySchema } = $props<{
    observation: ObservationType
    masterySchema: MasterySchemaWithConfig
  }>()

  const bgColor = $derived.by(() => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return null
    }
    return getMasteryLevelColorByValue(observation.masteryValue as number, masterySchema, 0.7)
  })

  const color = $derived(bgColor ? getContrastFriendlyTextColor(bgColor) : 'inherit')

  const masteryLevelTitle = $derived.by(() => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return null
    }
    return getMasteryTitleByValue(observation.masteryValue as number, masterySchema)
  })

  const isMasteryValueVisible = $derived.by(() => {
    if (!masterySchema || !isNumber(observation.masteryValue)) {
      return false
    }
    return masterySchema?.config?.isMasteryValueVisible ?? false
  })
</script>

<span class="masteryLevelTitle" style="background-color: {bgColor}; color: {color};">
  {masteryLevelTitle}
  {#if isMasteryValueVisible}
    [{observation.masteryValue}]
  {/if}
</span>

<style>
  .masteryLevelTitle {
    padding: 0.25rem 0.5rem 0.2rem 0.5rem;
    display: inline-block;
    font-size: inherit;
  }
</style>
