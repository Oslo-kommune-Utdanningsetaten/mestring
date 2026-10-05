<script lang="ts">
  import type { ObservationType } from '../../generated/types.gen'
  import { localStorage } from '../../stores/localStorage'

  let {
    observations = [],
    calculatePosition,
    orientation = 'vertical',
    inset = '0',
  }: {
    observations?: ObservationType[]
    calculatePosition: (value: number) => number
    orientation?: 'vertical' | 'horizontal'
    inset?: string
  } = $props()

  const isHistoryVisibleOnMasteryInput = localStorage<boolean>('isHistoryVisibleOnMasteryInput')
  const markerWidth = 4
  const maxMarkerBlur = 6

  const calculateMarkerBlur = (index: number) =>
    observations.length <= 1 ? 0 : maxMarkerBlur * (1 - index / (observations.length - 1))
</script>

{#if $isHistoryVisibleOnMasteryInput}
  <div class="observation-markers" style="inset: {inset};" aria-hidden="true">
    {#each observations as observation, index}
      {#if observation.masteryValue !== null && observation.masteryValue !== undefined}
        <div
          class="observation-marker"
          class:horizontal={orientation === 'horizontal'}
          style="--marker-position: {calculatePosition(
            observation.masteryValue
          )}px; --marker-width: {markerWidth}px; --marker-blur: {calculateMarkerBlur(index)}px;"
        ></div>
      {/if}
    {/each}
  </div>
{/if}

<style>
  .observation-markers {
    position: absolute;
    overflow: hidden;
    pointer-events: none;
  }

  .observation-marker {
    position: absolute;
    top: 0;
    left: var(--marker-position);
    height: 100%;
    width: var(--marker-width);
    transform: translateX(-50%);
    background-color: rgba(20, 20, 20, 0.3);
    filter: blur(var(--marker-blur));
  }

  .observation-marker.horizontal {
    top: var(--marker-position);
    left: 0;
    height: var(--marker-width);
    width: 100%;
    transform: translateY(-50%);
  }
</style>
