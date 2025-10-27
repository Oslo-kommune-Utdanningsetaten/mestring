<script lang="ts">
  const colors = ['#ffbe0b', '#fb5607', '#ff006e', '#8338ec', '#3a86ff', '#06d6a0']
  const burstCount = 14
  const bursts = Array.from({ length: burstCount }, (_, index) => {
    const angle = (360 / burstCount) * index
    const distance = 18 + (index % 3) * 8
    const color = colors[index % colors.length]
    return { angle, distance, color, index }
  })
</script>

<div class="goal-burst" aria-hidden="true">
  {#each bursts as burst}
    <span
      class="burst"
      style={`--burst-angle: ${burst.angle}deg; --burst-distance: ${burst.distance}px; --burst-color: ${burst.color}; --burst-index: ${burst.index};`}
    ></span>
  {/each}
</div>

<style>
  .goal-burst {
    --icon-size: 100%;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--icon-size);
    height: var(--icon-size);
    aspect-ratio: 1 / 1;
  }

  .goal-burst :global(svg) {
    width: 100%;
    height: 100%;
    transition:
      transform 180ms ease-out,
      filter 180ms ease-out;
  }

  .goal-burst:hover :global(svg),
  .goal-burst:focus-visible :global(svg) {
    transform: scale(1.08) rotate(-3deg);
    filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.15));
  }

  .burst {
    position: absolute;
    top: 50%;
    left: 50%;
    display: block;
    width: 4px;
    height: 12px;
    background: var(--burst-color);
    border-radius: 999px;
    opacity: 0;
    transform: translate(-50%, -50%) rotate(var(--burst-angle));
    pointer-events: none;
  }

  .goal-burst:hover .burst,
  .goal-burst:focus-visible .burst {
    animation: burst-pop 620ms ease-out forwards;
    animation-delay: calc(var(--burst-index) * 22ms);
  }

  @keyframes burst-pop {
    0% {
      opacity: 0;
      transform: translate(-50%, -50%) rotate(var(--burst-angle)) translateY(0) scale(0.4);
    }

    35% {
      opacity: 1;
      transform: translate(-50%, -50%) rotate(var(--burst-angle))
        translateY(calc(-0.6 * var(--burst-distance))) scale(1.05);
    }

    100% {
      opacity: 0;
      transform: translate(-50%, -50%) rotate(var(--burst-angle))
        translateY(calc(-1 * var(--burst-distance))) scale(0.75);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .goal-burst :global(svg) {
      transition: none;
    }

    .goal-burst:hover :global(svg),
    .goal-burst:focus-visible :global(svg) {
      transform: scale(1.03);
      filter: none;
    }

    .goal-burst:hover .burst,
    .goal-burst:focus-visible .burst {
      animation: none;
      opacity: 0;
    }
  }
</style>
