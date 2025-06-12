import { writable } from 'svelte/store'
import { pingRetrieve } from '../generated/sdk.gen'

export type ComponentStatus = 'unknown' | 'up' | 'down'

type ApiHealthStore = {
  api: ComponentStatus
  db: ComponentStatus
  isOk: boolean
}

const createApiHealthStore = () => {
  const { subscribe, update } = writable<ApiHealthStore>({
    api: 'up',
    db: 'up',
    isOk: true,
  })

  return {
    subscribe,
    checkHealth: async () => {
      try {
        const result: any = await pingRetrieve()
        const { response, data } = result
        if (response.status === 200) {
          const { api, db } = data as { api: ComponentStatus; db: ComponentStatus }
          const status = {
            api,
            db,
            isOk: api === 'up' && db === 'up',
          }
          update((): ApiHealthStore => status)
          return status
        } else {
          throw new Error(`Unexpected health status: ${response.status}`)
        }
      } catch (error) {
        update(() => ({
          api: 'down',
          db: 'unknown', // We don't know DB status if API is down
          isOk: false,
        }))
        return false
      }
    },
  }
}

export const apiHealth = createApiHealthStore()
