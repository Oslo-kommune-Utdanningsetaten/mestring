<script lang="ts">
  interface Props {
    min: number
    max: number
    value: number
  }

  let { min, max, value }: Props = $props()

  const clamp = (n: number, min: number, max: number) => Math.min(max, Math.max(min, n))
  const uid = Math.random().toString(36).slice(2, 8)

  // Normalized value (0-100) for easier calculations and rendering
  const normalizedValue = $derived(clamp(value, min, max))

  // Colors
  const colors = {
    body: '#F0A030',
    bodyDark: '#D48E28',
    spots: '#8B5E2B',
    hooves: '#5D4037',
    horn: '#C4923F',
    hornTip: '#8B5E2B',
    eye: '#2C1810',
    eyeHl: '#FFFFFF',
    innerEar: '#E8923A',
    mane: '#8B5E2B',
    shadow: '#9E9E9E',
  }

  // Neck tilt (12° forward lean)
  const TILT = (12 * Math.PI) / 180
  const sinTilt = Math.sin(TILT)
  const cosTilt = Math.cos(TILT)

  // Fixed body geometry
  const GROUND = 395
  const BODY_X = 148,
    BODY_Y = 285,
    BODY_RX = 72,
    BODY_RY = 44

  // Legs
  const LEG_TOP = 268,
    LEG_BOTTOM = 390,
    HOOF = 10
  const legsFar = [
    { x: 105, w: 14 }, // back far
    { x: 200, w: 14 }, // front far
  ]
  const legsNear = [
    { x: 93, w: 16 }, // back near
    { x: 188, w: 16 }, // front near
  ]

  // Neck (variable length)
  const NECK_X = 190,
    NECK_BASE_Y = 260
  const NECK_W_BASE = 34,
    NECK_W_TOP = 24
  const MIN_NECK = 35,
    MAX_NECK = 230

  const neckLen = $derived(MIN_NECK + (normalizedValue / max) * (MAX_NECK - MIN_NECK))
  const neckTopX = $derived(NECK_X + sinTilt * neckLen)
  const neckTopY = $derived(NECK_BASE_Y - cosTilt * neckLen)

  const neckPath = $derived(
    `M${NECK_X - NECK_W_BASE / 2},${NECK_BASE_Y} L${neckTopX - NECK_W_TOP / 2},${neckTopY} L${neckTopX + NECK_W_TOP / 2},${neckTopY} L${NECK_X + NECK_W_BASE / 2},${NECK_BASE_Y} Z`
  )

  // Head
  const HEAD_RX = 28,
    HEAD_RY = 18
  const headX = $derived(neckTopX + 12)
  const headY = $derived(neckTopY - HEAD_RY + 8)

  // Ossicones (horns)
  const hornLeft = $derived({
    x1: headX - 6,
    y1: headY - HEAD_RY + 2,
    x2: headX - 8,
    y2: headY - HEAD_RY - 13,
  })
  const hornRight = $derived({
    x1: headX + 6,
    y1: headY - HEAD_RY + 2,
    x2: headX + 4,
    y2: headY - HEAD_RY - 13,
  })

  // Ear
  const earPts = $derived(
    `${headX - HEAD_RX + 6},${headY - 4} ${headX - HEAD_RX - 6},${headY - 16} ${headX - HEAD_RX + 3},${headY - 18}`
  )
  const innerEarPts = $derived(
    `${headX - HEAD_RX + 7},${headY - 6} ${headX - HEAD_RX - 3},${headY - 15} ${headX - HEAD_RX + 4},${headY - 16}`
  )

  // Eye
  const eyeX = $derived(headX + 10)
  const eyeY = $derived(headY - 2)

  // Nostril & mouth
  const nostrilX = $derived(headX + HEAD_RX - 4)
  const nostrilY = $derived(headY + 2)
  const mouthPath = $derived(
    `M${headX + HEAD_RX - 20},${headY + 9} Q${headX + HEAD_RX - 14},${headY + 14} ${headX + HEAD_RX - 7},${headY + 9}`
  )

  // Tail
  const tailPath = 'M 81 277 C 68 262, 58 302, 64 324'

  // Body spots (fixed positions inside body ellipse)
  const bodySpots = [
    { cx: 115, cy: 272, r: 9 },
    { cx: 140, cy: 298, r: 8 },
    { cx: 168, cy: 269, r: 10 },
    { cx: 130, cy: 265, r: 7 },
    { cx: 164, cy: 302, r: 8 },
    { cx: 182, cy: 295, r: 7 },
    { cx: 108, cy: 288, r: 7 },
    { cx: 148, cy: 272, r: 6 },
    { cx: 188, cy: 278, r: 6 },
  ]

  // Neck spots (parametric along neck)
  const neckSpotDefinitions = [
    { t: 0.12, dx: 4, r: 5 },
    { t: 0.28, dx: -5, r: 4.5 },
    { t: 0.42, dx: 3, r: 5 },
    { t: 0.56, dx: -4, r: 4 },
    { t: 0.7, dx: 5, r: 5 },
    { t: 0.84, dx: -3, r: 4.5 },
    { t: 0.95, dx: 2, r: 4 },
  ]

  const neckSpots = $derived(
    neckSpotDefinitions
      .filter(spot => neckLen * spot.t > spot.r * 2.5)
      .map(spot => ({
        cx: NECK_X + sinTilt * neckLen * spot.t + spot.dx,
        cy: NECK_BASE_Y - cosTilt * neckLen * spot.t,
        r: spot.r,
      }))
  )

  // Head spots
  const headSpots = $derived([
    { cx: headX - 12, cy: headY - 4, r: 3.5 },
    { cx: headX + 3, cy: headY - 10, r: 3 },
    { cx: headX - 6, cy: headY + 7, r: 3 },
  ])

  // Mane (triangular tufts along back of neck)
  const maneTufts = $derived.by(() => {
    const count = Math.max(2, Math.floor(neckLen / 22)) - 1
    const tOffset = 14 / neckLen
    return Array.from({ length: count }, (_, index) => {
      const t1 = tOffset + (index / count) * (1 - tOffset)
      const t2 = tOffset + ((index + 0.5) / count) * (1 - tOffset)
      const t3 = tOffset + ((index + 1) / count) * (1 - tOffset)
      const w1 = NECK_W_BASE + (NECK_W_TOP - NECK_W_BASE) * t1
      const w2 = NECK_W_BASE + (NECK_W_TOP - NECK_W_BASE) * t2
      const w3 = NECK_W_BASE + (NECK_W_TOP - NECK_W_BASE) * t3
      return `${NECK_X + sinTilt * neckLen * t1 - w1 / 2},${NECK_BASE_Y - cosTilt * neckLen * t1} ${NECK_X + sinTilt * neckLen * t2 - w2 / 2 - 7},${NECK_BASE_Y - cosTilt * neckLen * t2} ${NECK_X + sinTilt * neckLen * t3 - w3 / 2},${NECK_BASE_Y - cosTilt * neckLen * t3}`
    })
  })

  // --- Max rendered height (px) of the giraffe container ---
  const MAX_HEIGHT = 400

  // ViewBox: fixed height (tallest giraffe), variable width
  const VIEW_TOP = -18
  const VIEW_HEIGHT = GROUND + 12 - VIEW_TOP // ~425
  const vbLeft = $derived(Math.min(headX - HEAD_RX - 20, 20))
  const vbWidth = $derived(Math.max(260, headX + HEAD_RX + 20 - vbLeft))
  const viewBox = $derived(`${vbLeft} ${VIEW_TOP} ${vbWidth} ${VIEW_HEIGHT}`)
</script>

<svg {viewBox} xmlns="http://www.w3.org/2000/svg" style="height: {MAX_HEIGHT}px; width: auto;">
  <defs>
    <clipPath id={`b-${uid}`}>
      <ellipse cx={BODY_X} cy={BODY_Y} rx={BODY_RX} ry={BODY_RY} />
    </clipPath>
    <clipPath id={`n-${uid}`}>
      <path d={neckPath} />
    </clipPath>
    <clipPath id={`h-${uid}`}>
      <ellipse cx={headX} cy={headY} rx={HEAD_RX} ry={HEAD_RY} />
    </clipPath>
  </defs>

  <!-- Ground shadow -->
  <ellipse cx={BODY_X} cy={GROUND - 1} rx={65} ry={4} fill={colors.shadow} opacity="0.2" />

  <!-- Far legs (behind body) -->
  {#each legsFar as leg}
    <rect
      x={leg.x}
      y={LEG_TOP}
      width={leg.w}
      height={LEG_BOTTOM - LEG_TOP}
      rx={4}
      fill={colors.bodyDark}
    />
    <rect
      x={leg.x - 1}
      y={LEG_BOTTOM - HOOF}
      width={leg.w + 2}
      height={HOOF}
      rx={3}
      fill={colors.hooves}
    />
  {/each}

  <!-- Tail -->
  <path d={tailPath} fill="none" stroke={colors.spots} stroke-width="3" stroke-linecap="round" />
  <ellipse cx={64} cy={328} rx="5" ry="8" fill={colors.spots} />

  <!-- Body -->
  <ellipse cx={BODY_X} cy={BODY_Y} rx={BODY_RX} ry={BODY_RY} fill={colors.body} />

  <!-- Near legs (in front of body) -->
  {#each legsNear as leg}
    <rect
      x={leg.x}
      y={LEG_TOP}
      width={leg.w}
      height={LEG_BOTTOM - LEG_TOP}
      rx={4}
      fill={colors.body}
    />
    <rect
      x={leg.x - 1}
      y={LEG_BOTTOM - HOOF}
      width={leg.w + 2}
      height={HOOF}
      rx={3}
      fill={colors.hooves}
    />
  {/each}

  <!-- Body spots -->
  <g clip-path={`url(#b-${uid})`}>
    {#each bodySpots as s}
      <circle cx={s.cx} cy={s.cy} r={s.r} fill={colors.spots} opacity="0.6" />
    {/each}
  </g>

  <!-- Neck -->
  <path d={neckPath} fill={colors.body} />

  <!-- Neck spots -->
  <g clip-path={`url(#n-${uid})`}>
    {#each neckSpots as s}
      <circle cx={s.cx} cy={s.cy} r={s.r} fill={colors.spots} opacity="0.6" />
    {/each}
  </g>

  <!-- Mane -->
  {#each maneTufts as pts}
    <polygon points={pts} fill={colors.mane} opacity="0.75" />
  {/each}

  <!-- Head -->
  <ellipse cx={headX} cy={headY} rx={HEAD_RX} ry={HEAD_RY} fill={colors.body} />

  <!-- Head spots -->
  <g clip-path={`url(#h-${uid})`}>
    {#each headSpots as s}
      <circle cx={s.cx} cy={s.cy} r={s.r} fill={colors.spots} opacity="0.5" />
    {/each}
  </g>

  <!-- Ear -->
  <polygon points={earPts} fill={colors.body} />
  <polygon points={innerEarPts} fill={colors.innerEar} opacity="0.5" />

  <!-- Ossicones (horns) -->
  <line
    x1={hornLeft.x1}
    y1={hornLeft.y1}
    x2={hornLeft.x2}
    y2={hornLeft.y2}
    stroke={colors.horn}
    stroke-width="3"
    stroke-linecap="round"
  />
  <circle cx={hornLeft.x2} cy={hornLeft.y2} r="3.5" fill={colors.hornTip} />
  <line
    x1={hornRight.x1}
    y1={hornRight.y1}
    x2={hornRight.x2}
    y2={hornRight.y2}
    stroke={colors.horn}
    stroke-width="3"
    stroke-linecap="round"
  />
  <circle cx={hornRight.x2} cy={hornRight.y2} r="3.5" fill={colors.hornTip} />

  <!-- Eye -->
  <circle cx={eyeX} cy={eyeY} r="4" fill={colors.eye} />
  <circle cx={eyeX + 1.2} cy={eyeY - 1} r="1.5" fill={colors.eyeHl} />

  <!-- Nostril -->
  <circle cx={nostrilX} cy={nostrilY} r="1.8" fill={colors.spots} opacity="0.7" />

  <!-- Mouth -->
  <path d={mouthPath} fill="none" stroke={colors.spots} stroke-width="1.5" stroke-linecap="round" />
</svg>
