<script lang="ts">
  interface Props {
    onAction: () => void
    onAbort: () => void
    delay?: number // seconds until the action is executed
    buttonText?: string
  }

  const defaultDelay = 4
  const {
    onAction,
    delay = defaultDelay,
    onAbort,
    buttonText = 'Avbryt sletting',
  }: Props = $props()

  let secondsLeft = $state(0)
  let intervalId: ReturnType<typeof setInterval> | null = $state(null)
  let isActive = $state(false)
  const title = $derived<string>(`Sletting om ${secondsLeft} sekunder. Trykk for å avbryte.`)

  const startCountdown = () => {
    intervalId = setInterval(() => {
      secondsLeft--
      if (secondsLeft <= 0) {
        clearCountdown()
        isActive = false
        onAction()
      }
    }, 1000)
  }

  const clearCountdown = () => {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  const handleAbort = () => {
    clearCountdown()
    isActive = false
    secondsLeft = 0
    onAbort()
  }

  $effect(() => {
    secondsLeft = delay
    isActive = true
    startCountdown()
  })
</script>

{#if isActive}
  <button
    class="delayed-action"
    style="--delay: {delay}s"
    {title}
    onclick={handleAbort}
    onkeydown={e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleAbort()
      }
    }}
  >
    <span class="button-text">{buttonText}</span>
  </button>
{/if}

<style>
  @keyframes fill-progress {
    to {
      width: 100%;
    }
  }

  @keyframes reveal-white-text {
    to {
      clip-path: inset(0);
    }
  }

  .delayed-action {
    position: relative;
    overflow: hidden;
    background: var(--pkt-color-signal-red-100, #fde8e8);
    color: var(--pkt-color-signal-red-900, #8b0000);
    border: 1px solid var(--bs-gray);
    border-radius: 3px;
    margin-left: 8px;
  }

  .delayed-action:hover {
    filter: brightness(80%);
  }

  .button-text {
    position: relative;
    z-index: 2;
  }

  .button-text::before {
    content: 'Avbryt sletting';
    position: absolute;
    left: 0;
    color: white;
    animation: reveal-white-text var(--delay) linear forwards;
    clip-path: inset(0 100% 0 0);
  }

  .delayed-action::before {
    content: '';
    position: absolute;
    inset: 0;
    width: 0;
    background: var(--pkt-color-signal-red-500, #e02020);
    animation: fill-progress var(--delay) linear forwards;
    z-index: 1;
  }
</style>
