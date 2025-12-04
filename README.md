#### Hanabi_DS
### Group Members

[Blagoja Savevski] — blagoja.savevski@studio.unibo.it
[Pengyue Xu] - pengyue.xu@studio.unibo.it
[Gabriele Santi] - gabriele.santi6@studio.unibo.it
### Vision
Hanabi is a cooperative multiplayer card game for 2-5 players where players score by guessing their own hidden cards based on hints given by other players. This project aims to implement a working version of the game that manages the shared state consistently and reliably, while being able to tolerate disconnects from a client or the server. Players request to connect their clients to a server by joining a lobby with multiple queues based on the game player count. Each game is uniquely identified so it can be stored for a future restart if need be. Availability and fault tolerance of the spawned server is guaranteed by replicas of the server that in case of failure can be promoted to master and continue the game. Proper transfer of state with up to date moves is ensured to that the transition from one server to another seems seamless to the clients. The rules of the game are provided for reference: 
https://cdn.1j1ju.com/medias/b3/a9/0e-hanabi-rulebook.pdf. 
The goal is to build a working multiplayer Hanabi board-game platform through a incremental development process where each component can be isolated and tested to predict how it will interact with the others. 
### Motivation 
- #### Consistency: 
	The state of the game is kept replicated in a Redis Sentinel replica so that issues can be hidden from the client side as much as possible, as limited by the CAP theorem. Each turn clients get the state broadcasted by the server which ensures they all see the same state. The clients in turn execute a type of remote procedure call upon the state of the server with different functions depending on the rules of the game. Read-after-write consistency and write ordering (turn order) is guaranteed by having a single client being permitted to write at the same time. 
- #### Fault tolerance:
	In case of server fault, one of multiple Redis replicas in a single-leader system, when consensus is achieved through a vote, is promoted to master replica. The replicas would ideally be on other nodes so that failure does not affect them. At least one replica will be synchronously updated by the master.  After disconnect is detected, clients get informed who the new master is by the failover service. A client side timeout can result in the game continuing on without that player or ending there. 
- #### Scalability:
   Multiple instances of game servers can get deployed and work in parallel. The scope for scalability is limited and so a simpler but less expandable deployment method will be used.
- #### Concurrency:
   The server handles multiple connections concurrently with the clients by multi-threading. Likewise, the matchmaker handles the lifecycle of the server objects and related instances in a concurrent way. 
- #### Distributed deployment:
   All services - client, server, replicas are deployed as containers. Standardized protocol communication guarantees they interact in a predictable way. 
### Technologies used
- Back-end: Python, FastAPI 
- Front-end: HTML/CSS/JS 
- Networking: WebSockets 
- Deployment: Docker Compose, Redis Sentinel 
- Database: Redis
Changes to the stack might be made during development and subsequently  communicated. 
### Deliverables
- Source code 
- Instructions to deploy all services and test features
- Brief demo 
