import type { AactConfig } from 'aact'

/**
 * Rules are selected for a container-level C4 model of a modular monolith.
 * Service-level rules such as API Gateway and Common Reuse would be misleading
 * until the system is intentionally split into microservices.
 */
const config: AactConfig = {
  source: {
    type: 'plantuml',
    path: './docs/architecture/container.puml',
  },
  rules: {
    acl: false,
    acyclic: true,
    apiGateway: false,
    crud: false,
    dbPerService: true,
    cohesion: false,
    stableDependencies: false,
    commonReuse: false,
  },
}

export default config
