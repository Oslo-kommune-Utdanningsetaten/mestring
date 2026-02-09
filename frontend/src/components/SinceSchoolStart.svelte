<script lang="ts">
  const { dateAsString } = $props<{
    dateAsString?: string
  }>()

  const distanceInPercentSinceLastAugust = () => {
    const now = new Date()
    const august = new Date(now.getFullYear(), 7, 1) // August 1st of current year
    if (now < august) {
      // If we're earlier than august, use augustg from last year
      august.setFullYear(august.getFullYear() - 1)
    }
    const totalTime = now.getTime() - august.getTime()
    const elapsedTime = new Date(dateAsString).getTime() - august.getTime()
    return Math.min(Math.max(elapsedTime / totalTime, 0), 1) // Clamp between 0 and 1
  }
</script>

{#if dateAsString}
  <div>
    <span class="indicator" style="left: {distanceInPercentSinceLastAugust() * 100}%"></span>
  </div>
{/if}

<style>
  div {
    position: relative;
    font-size: 0.875rem;
    color: var(--pkt-color-grays-gray-600);
    border: 1px solid var(--pkt-color-grays-gray-300);
    width: 100%;
    min-height: 1.2rem;
  }

  .indicator {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 2px;
    background-color: var(--pkt-color-grays-gray-500);
  }
</style>
