For each step of the provided plan you should:
- Call the appropriate function with the required arguments, corresponding directly to the outlined plan's next action.
- Evaluate the function call's result and adjust the next steps accordingly, maintaining fidelity to the plan's intended sequence.
- If a function call fails or produces undesired outcomes, try to solve the problem by fining the reason of the fail and selecting workaround path.
- Persist through different strategies, avoiding repetition of unsuccessful attempts, until the task is completed.
- If you are stuck, do not try to repeat the request, as it will not help. Instead, try to explore the reason for the failure, modify the input or rollback some previous actions which led to the error.
- Document solely the function calls and their outcomes. Refrain from additional commentary or explanatory text during this execution phase.
Begin execution with the plan start point, adhering strictly to the prescribed operations. 
The project’s template root directory has already been created, so you don't need to create it. Produce files inside this directory. Treat it as the root directory and use relative paths starting with an empty string ''.

############ 
Example 1:

DESCRIPTION:
Generate template for project named `ktor-samples__chat` which should be mainly written on Kotlin programing language and aligns following description: 
A chat application written with Ktor using WebSockets and Sessions.

PLAN:
Detailed Step-by-Step Action Plan for Generating the Project Template
1. Define the Project Directory Structure
2. Generate files content and Write Files

EXECUTION:
1. Using function calling invoke `create-project-tree` function with `parentDirectory` argument is "" and `tree_structure` argument equals to
```
ktor-samples__chat/
├── README.md
├── build.gradle
├── tests/
└── src/
    ├── backendMain/
    │     ├── kotlin/
    │     │     ├── ChatApplication.kt
    │     │     └── ChatServer.kt
    │     └── resources/
    │         ├── application.conf
    │         ├── logback.xml
    │         └── web/
    │             └── index.html
    ├── backendTest/
    │     └── kotlin/
    │         └── ChatApplicationTest.kt
    └── frontendMain/
        └── kotlin/
            └── main.kt
```
Make sure your tree in format of command line tool tree format and contains only │├└ and ─ symbols for brunch drawing

2. For each file in file tree using function calling invoke `set-file-text` function. 
For example, you can start with `filePath` argument equals to 'ktor-samples__chat/chat/src/backendMain/kotlin/ChatApplication.kt' and `text` equals to 
```
package io.ktor.samples.chat.backend

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.http.content.*

fun main() {
    embeddedServer(Netty, port = 8080) {
        ChatApplication().apply { main() }
    }.start(wait = true)
}
```