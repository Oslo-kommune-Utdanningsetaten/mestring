import { client } from '../api/client.gen'

client.setConfig({
  baseUrl: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'Bearer <token_from_service_client>', // TODO: replace with actual token
  },
})

client.interceptors.response.use(response => {
  if (response.status === 200) {
    console.log(`request to ${response.url} was successful`)
  }
  return response
})

export default client
