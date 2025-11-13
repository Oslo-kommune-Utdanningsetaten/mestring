import { writable, get } from 'svelte/store'

type AlertType = {
  id?: number
  timestamp?: number
  type: string
  message: string
  isPersistent?: boolean
}

const alertTTL = 5 * 1000 // time to live for non-persistent alerts in milliseconds

let nextAlertId = 0

// Create a store to track alerts
export const alerts = writable<AlertType[]>([])

export const addAlert = (newAlert: AlertType) => {
  newAlert.id = ++nextAlertId
  newAlert.timestamp = Date.now()
  alerts.update(currentAlerts => [...currentAlerts, newAlert])
}

export const removeAlert = (id?: number) => {
  if (id === undefined) return
  alerts.update(currentAlerts => currentAlerts.filter(alert => id !== alert.id))
}

// every 5 seconds, remove non-persistent alerts older than 10 seconds
setInterval(() => {
  const now = Date.now()
  alerts.update(currentAlerts =>
    currentAlerts.filter(alert => alert.isPersistent || now - alert.timestamp < alertTTL)
  )
}, alertTTL)
