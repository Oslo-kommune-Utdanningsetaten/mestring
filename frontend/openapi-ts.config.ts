import { defaultPlugins } from '@hey-api/openapi-ts'

export default {
  input: 'http://localhost:5000/api/schema',
  output: 'src/api',
  plugins: [
    ...defaultPlugins,
    {
      name: '@hey-api/client-fetch',
    },
    {
      enums: false, // default
      name: '@hey-api/typescript',
    },
  ],
}
