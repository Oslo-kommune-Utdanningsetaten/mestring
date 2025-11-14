import { writable, get } from 'svelte/store'

type AlertType = {
  id: number
  timestamp: number
  type: string
  message: string
  isPersistent: boolean
}

const alertTTL = 5 * 1000 // time to live for non-persistent alerts in milliseconds
const alertFlushInterval = 3 * 1000 // interval to flush old alerts

let nextAlertId = 0

// Create a store to track alerts
export const alerts = writable<AlertType[]>([])

export const addAlert = (newAlert: Partial<AlertType>) => {
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
