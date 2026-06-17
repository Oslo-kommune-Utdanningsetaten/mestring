<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../../types/models'
  import { useMasteryCalculations, calculateTrendFraction } from '../../utils/masteryHelpers'

  const {
    masteryData,
    masterySchema,
    isBadgeEmpty = false,
    isBadgeVoid = false,
    isLastValueVisible = true,
  } = $props<{
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    isBadgeEmpty?: boolean
    isBadgeVoid?: boolean
    isLastValueVisible?: boolean
  }>()

  const trend = $derived(masteryData?.trend ?? 0)
  const title = $derived(
    [masterySchema?.title, masteryData?.title, 'Trend: ' + trend].filter(Boolean).join('\n')
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))

  // Trend
  const isFlat = $derived(Math.abs(trend) < calculations.flatTrendThreshold)
  const isDecreasing = $derived(trend < 0 && !isFlat)

  // Dimensions
  const size = 30
  const center = size / 2
  const faceRadius = 14
  const mouthHalfWidth = 7
  const mouthY = 19
  const eyeOffsetX = 5 // horizontal distance of each eye from centre
  const eyeY = 11
  const eyeRadius = 1.5

  // Hair: strands grow downward from the top of the circle into the face.
  const maxHairHeight = 10 // px at max score
  const hairStrandCount = 7 // number of strands, evenly sprouting from the circle
  const hairSpreadDeg = 100 // total angular spread of the strands across the top

  // Largest central angle the mouth arc may reach (kept below 180° => minor arc)
  const maxMouthAngle = (160 * Math.PI) / 180

  // Trend is change in mastery value over time.
  const trendFraction = $derived(calculateTrendFraction(trend, calculations.deltaValue))

  // The mouth is a minor arc whose central angle grows with the trend magnitude.
  // Positive trend bulges the arc downwards (smile), negative bulges it up (frown).
  const mouthPath = $derived.by(() => {
    const x1 = center - mouthHalfWidth
    const x2 = center + mouthHalfWidth
    if (isFlat) {
      return `M ${x1} ${mouthY} L ${x2} ${mouthY}`
    }
    const chord = mouthHalfWidth * 2
    const angle = trendFraction * maxMouthAngle
    const radius = chord / (2 * Math.sin(angle / 2))
    const sweepFlag = isDecreasing ? 1 : 0 // 1 => smile (curves up), 0 => frown (curves down)
    const modifiedMouthY = isDecreasing ? mouthY + 3 : mouthY
    return `M ${x1} ${modifiedMouthY} A ${radius} ${radius} 0 0 ${sweepFlag} ${x2} ${modifiedMouthY}`
  })

  // Calculate hair height based on latest mastery observation
  const masteryFraction = $derived(
    calculations.maxValue > 0
      ? Math.min(Math.max((masteryData?.mastery ?? 0) / calculations.maxValue, 0), 1)
      : 0
  )
  const hairHeight = $derived(masteryFraction * maxHairHeight)

  // Strands are rooted on the circle's surface across the top arc and grow
  // downward into the face. They share the same length, which encodes the
  // mastery value.
  const hairStrands = $derived.by(() => {
    const startDeg = -hairSpreadDeg / 2
    const stepDeg = hairStrandCount > 1 ? hairSpreadDeg / (hairStrandCount - 1) : 0
    return Array.from({ length: hairStrandCount }, (_, i) => {
      const rad = ((startDeg + i * stepDeg) * Math.PI) / 180
      const x = center + faceRadius * Math.sin(rad)
      const baseY = center - faceRadius * Math.cos(rad)
      return { x, baseY, tipY: baseY + hairHeight }
    })
  })
</script>

<span class="badge-container d-inline-flex align-items-center" {title}>
  <svg class="trend-box" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
    <circle class="face" cx={center} cy={center} r={faceRadius} />
    {#if masteryData}
      <!-- draw a face-->
      {#if isLastValueVisible}
        {#each hairStrands as strand}
          <line class="hair" x1={strand.x} y1={strand.baseY} x2={strand.x} y2={strand.tipY} />
        {/each}
      {/if}
      <!-- eyes-->
      <circle class="eye" cx={center - eyeOffsetX} cy={eyeY} r={eyeRadius} />
      <circle class="eye" cx={center + eyeOffsetX} cy={eyeY} r={eyeRadius} />
      <!-- mouth-->
      <path class="mouth" d={mouthPath} />
    {:else if isBadgeEmpty}
      <!-- just a blank face-->
      <title>Observasjoner mangler</title>
    {:else if isBadgeVoid}
      <!-- hatched pattern-->
      <title>Mål mangler</title>
      <defs>
        <pattern
          id="void-hatch"
          width="4"
          height="4"
          patternUnits="userSpaceOnUse"
          patternTransform="rotate(45)"
        >
          <rect width="4" height="4" fill="white" />
          <rect width="2" height="4" fill="color-mix(in srgb, var(--bs-gray) 50%, transparent)" />
        </pattern>
      </defs>
      <circle cx={center} cy={center} r={faceRadius} fill="url(#void-hatch)" />
    {/if}
  </svg>
</span>

<style>
  .badge-container {
    position: relative;
    display: inline-block;
    height: 30px;
    background-color: transparent;
  }

  .face {
    fill: none;
    stroke: var(--bs-dark);
    stroke-width: 1;
  }

  .hair {
    stroke: rgba(var(--bs-dark-rgb), 0.5);
    stroke-width: 1.5;
    stroke-linecap: round;
  }

  .eye {
    fill: var(--bs-dark);
    stroke: none;
  }

  .mouth {
    fill: none;
    stroke: var(--bs-dark);
    stroke-width: 1.5;
    stroke-linecap: round;
  }
</style>
