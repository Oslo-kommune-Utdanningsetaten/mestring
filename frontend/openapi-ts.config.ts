import { defaultPlugins } from '@hey-api/openapi-ts'

export default {
  input: 'http://localhost:5000/api/schema',
  output: 'src/generated',
  parser: {
    transforms: {
      readWrite: {
        responses: '{{name}}',
        requests: '{{name}}Create',
      },
    },
  },
  plugins: [
    ...defaultPlugins,
    {
      name: '@hey-api/client-fetch',
      baseUrl: '/',
    },
    {
      enums: false,
      name: '@hey-api/typescript',
      definitions: {
        name: '{{name}}Type',
      },
    },
  ],
}
