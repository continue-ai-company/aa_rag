from quart import Quart, request, jsonify
import secrets
import string
import rag

apiReg = {}  # API register map
apiQs = {}  # API Q-List map:
callQResults = {}  # API Q-Call result map for retrieve
callSeq = 0
callingQAPIs = {}

# If current msg-task is free, call it.
async def maybeCall(msg):
    stub=callingQAPIs.get(msg)
    if(stub):
        return # Task is busy
    list = apiQs.get(msg)
    if (not list):
        return
    stub = list.pop()
    if("aborted" in stub):
        maybeCall(msg)
        return
    callingQAPIs[msg]=stub
    func = apiReg[msg]
    try:
        result = await func(stub["data"])
    except Exception as e:
        result = {"code": 500, "error": e}
    if(not ("aborted" in stub)):
        callQResults[stub["callId"]] = result # TODO: setTimeout?
    callingQAPIs.pop(msg)
    maybeCall(msg)


async def callQAPI(data):
    if (not "msg" in data):
        return jsonify({"code": 500, "info": "Missing message: msg"})
    msg = data["msg"]
    if (not msg in apiQs):
        apiQs[msg] = []
    list = apiQs[msg]
    callId = genCallId()
    list.append({"data": data, "callId": callId})
    maybeCall(msg)
    return {"code": 200, "msg": msg, "callId": callId}


async def checkQAPI(data): # check if Q-API-Call is done
    if (not "callId" in data):
        return {"code": 400, "info": "Missing callId"}
    callId = data["callId"]
    if (not callId in callQResults):
        return {"code": 200, "info": "Waiting"}
    result = callQResults[callId]
    callQResults.pop(callId)
    return {"code": 200, "result": result}


async def abortQAPI(data): # Abort a Q-API-Call:
    msg = data.get("msg")
    if (not msg):
        return {"code": 400, "info": "Missing msg"}
    callId = data.get("callId")
    if (not callId):
        return {"code": 400, "info": "Missing callId"}
    stub=callingQAPIs[msg]
    if(stub):
        stub["aborted"]=True
        return {"code": 200}
    list = callQResults.get(msg)
    if (not list):
        return {"code": 200}
    for stub in list:
        if stub['callId'] == callId:
            stub.aborted=True
            return {"code": 200}
    stub=callQResults.get(callId)
    if(stub):
        callQResults.pop(callId)
    return {"code": 200}

def generate_token(length):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

def genCallId():
    global callSeq
    callSeq = callSeq + 1
    return generate_token(8) + "_" + callSeq;

app = Quart(__name__)

@app.route('/api', methods=['POST'])
async def process_json():
    data = await request.get_json()

    if (not "msg" in data):
        return jsonify({"code": 500, "info": "Missing message: msg"})
    msg = data["msg"]

    if (not msg in apiReg):
        return jsonify({"code": 500, "info": f"API '{msg}' not found."})

    func = apiReg[msg]
    if (func != None):
        response = await func(data)
        return response

    # Handler not found:
    response = {
        "code": 500,
        "message": f"{msg} is not found"
    }
    return jsonify(response)


@app.route('/qapi', methods=['POST'])
async def process_q_call():
    op = None
    data = await request.get_json()

    if (not "op" in data):
        return jsonify({"code": 500, "info": "Missing operator: op"})
    op = data["op"]

    # Call, make it in Q:
    if (op == "call"):
        return await callQAPI(data)
    if (op == "check"):
        return await checkQAPI(data)
    if (op == "abort"):
        return await abortQAPI(data)
    # Operator not available:
    response = {
        "code": 500,
        "message": f"Operator {op} is not available"
    }
    return jsonify(response)

# TODO: Scan dir for handler
rag.regAPI(apiReg)

if __name__ == '__main__':
    app.run(port=5050)
