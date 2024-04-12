
'''
main will check if the active cores are busy or idle if busy check if num of logic cores is = the max cores if not then create a new process 
and add it to the active_processes list. If idle then pass the new connection to it. othrewise pass the connection to the manager process. 
the manager will add the connection to the queue it will also look over the queue and check if the connection has been in the queue for more 
than 10 seconds if they have then remove then from the queue and send a response to the connection. when a logic core is done processing the connection
it will send a response to the connection and remove it from the active_processes list. then go to the queue and pull a new connection if there is none
then the logic core will add itself to a list of idle cores as well as the time it went idle, then the manager will check the list and any core that have 
been idle for more than 30 seconds will be terminated. the list of idle cores will also be used by the main to check if there are any idle cores and if there are
then it will pass the new connection to the idle core.

Main Process:

Check the status of active logic cores.
If any logic core is idle, pass the new connection to it.
If all logic cores are busy, check if the number of logic cores equals the maximum allowed cores.
If not, create a new logic core (process) and add it to the active_processes list.
Otherwise, pass the connection to the manager process.


Manager Process:

Manage a queue of connections.
Check the queue regularly.
If a connection has been in the queue for more than 10 seconds, remove it from the queue and send a response to the connection.
If a logic cores


Logic Cores (Worker Processes):

Handle connections asynchronously.
Send responses back to the connections.
When a logic core finishes processing a connection, remove it from the active_processes list.
Check the queue for new connections.
If no connections are available, add itself to a list of idle cores along with the time it went idle.

Idle Core Management:

The manager process periodically checks the list of idle cores.
If any core has been idle for more than 30 seconds, terminate it.

Utilization:

The main process uses the list of idle cores to determine if there are any available to handle new connections.

