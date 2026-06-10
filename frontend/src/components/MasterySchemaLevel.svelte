<script lang="ts">
  import type { MasterySchemaWithConfig } from '../types/models'
  import { dataStore } from '../stores/data'
  import { getMasteryLevelColorByValue, getMasteryTitleByValue } from '../utils/masteryHelpers'
  import { getContrastFriendlyTextColor } from '../utils/functions'

  // Supports both passing the whole schema or just the schema ID, because we might want to render a badge based on a schema which is not associated with currentSchool
  const {
    masteryValue,
    masterySchemaId = null,
    masterySchema = null,
  } = $props<{
    masteryValue: number | null | undefined
    masterySchemaId?: string | null | undefined
    masterySchema?: MasterySchemaWithConfig | null
  }>()

  const resolvedSchema = $derived(
    masterySchema ||
      ($dataStore.masterySchemas.find(s => s.id === masterySchemaId) as
        | MasterySchemaWithConfig
        | undefined)
  )

  const title = $derived(
    resolvedSchema && masteryValue != null
      ? getMasteryTitleByValue(masteryValue, resolvedSchema)
      : ''
  )

  const boxColor = $derived(
    resolvedSchema && masteryValue !== null
      ? getMasteryLevelColorByValue(masteryValue, resolvedSchema)
      : 'rgba(100, 100, 100)'
  )

  const textColor = $derived(getContrastFriendlyTextColor(boxColor))

  const longestTitle = $derived.by(() => {
    const levels = resolvedSchema?.config?.levels
    if (!levels) return ''
    return levels.reduce(
      (longest: string, level: { title: string }) =>
        level.title.length > longest.length ? level.title : longest,
      ''
    )
  })

  $effect(() => {
    if (!resolvedSchema) {
      console.warn('MasteryBadge: masterySchemaId is null or undefined')
    }
  })
</script>

{#if resolvedSchema}
  <span class="mastery-badge" style="background-color: {boxColor}; color: {textColor}">
    <span class="sizer">{longestTitle}</span>
    <span class="label">{title}</span>
  </span>
{/if}

<style>
  .mastery-badge {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 8px;
    border-radius: 2px;
    height: 30px;
    min-width: 30px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
  }

  .sizer {
    visibility: hidden;
  }

  .label {
    position: absolute;
  }
</style>
