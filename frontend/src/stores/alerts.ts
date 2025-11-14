import { writable, get } from 'svelte/store'

type alertTypeType = 'success' | 'info' | 'warning' | 'danger' // not 100% happy with alertTypeTypeType, but hey :/

type AlertType = {
  id: number
  timestamp: number
  type: alertTypeType
  message: string
  isPersistent: boolean
}

const alertTTL = 10 * 1000 // Keep non-persistent alerts visible for 10 seconds
const alertFlushInterval = 5 * 1000 // Check if old alerts should be removed every 5 seconds

let nextAlertId = 0

// Store to track alerts
export const alerts = writable<AlertType[]>([])

export const addAlert = (newAlert: Partial<AlertType>) => {
  // Don't add alert to store if we already have one with same message
  if (get(alerts).some(alert => alert.message === newAlert.message)) return
  newAlert.id = ++nextAlertId
  newAlert.timestamp = Date.now()
  newAlert.isPersistent = newAlert.isPersistent || false
  alerts.update(currentAlerts => [...currentAlerts, newAlert as AlertType])
}

export const removeAlert = (id?: number) => {
  if (id === undefined) return
  alerts.update(currentAlerts => currentAlerts.filter(alert => id !== alert.id))
}

// every alertFlushInterval, remove non-persistent alerts older than alertTTL
setInterval(() => {
  const now = Date.now()
  alerts.update(currentAlerts =>
    currentAlerts.filter(alert => alert.isPersistent || now - alert.timestamp < alertTTL)
  )
}, alertFlushInterval)
