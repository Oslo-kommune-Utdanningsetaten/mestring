<script lang="ts">
  import type { StatusType } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { dataStore } from '../stores/data'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'
  import { getContrastFriendlyTextColor } from '../utils/functions'

  const { status } = $props<{
    status: StatusType
  }>()

  const masterySchema = $derived(
    $dataStore.masterySchemas.find(s => s.id === status.masterySchemaId) as
      | MasterySchemaWithConfig
      | undefined
  )

  const title = $derived(
    masterySchema && status.masteryValue != null
      ? getMasteryTitleByValue(status.masteryValue, masterySchema)
      : ''
  )

  const boxColor = $derived(
    masterySchema && status.masteryValue != null
      ? getMasteryLevelColorByValue(status.masteryValue, masterySchema)
      : 'rgba(100, 100, 100)'
  )

  const textColor = $derived(getContrastFriendlyTextColor(boxColor))
</script>

<span title={status.id} class="status-tag" style="background-color: {boxColor}; color: {textColor}">
  {title}
</span>

<style>
  .status-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding-top: 1px;
    border-radius: 2px;
    width: 30px;
    height: 30px;
    font-size: 0.8rem;
    font-weight: 600;
    overflow: hidden;
  }
</style>
