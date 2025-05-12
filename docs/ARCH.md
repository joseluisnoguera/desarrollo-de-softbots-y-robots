## Arquitectura (IN PROGRESS)

```mermaid
architecture-beta
    group api(cloud)[VPC]

    service db(server)[Hotel API] in api
    service disk1(disk)[Vector Database] in api
    service disk2(disk)[API Database] in api
    service server(server)[Agent] in api

    db:L -- R:server
    disk1:T -- B:server
    disk2:T -- B:db
```