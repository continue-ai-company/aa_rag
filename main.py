import os
import asyncio
import session

pathLib=os.path

# Get current path:
current_path = pathLib.dirname(pathLib.realpath(__file__))
print("Run path:", current_path)

#Create session object as agent runtime:
ssn=session.AISession(current_path)
ssn.showVersion()
print("")

#Setup an async looper for async calls:
loop = asyncio.get_event_loop()

#excute your agent:
result=loop.run_until_complete(ssn.execAgent("agent.py","hello!"))
print(result)
