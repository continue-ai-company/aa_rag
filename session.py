import os
from io import BytesIO
import base64
import json
import curses
import importlib
import importlib.util
from PIL import Image
from openai import OpenAI
from playsound import playsound
from datetime import datetime

pathLib=os.path

#Replace your OpenAI key here:
openAI=OpenAI(api_key="[YOUR-OPENAI-KEY]");

def import_module_from_file(file_path):
	name=pathLib.basename(file_path)
	if(name.endswith(".py")):
		name=name[:-3]
	spec = importlib.util.spec_from_file_location(name, file_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module

class AISession:
	basePath=None
	curAgent=None
	curPath=None
	agentDict={}
	globalContext={}
	
	def __init__(self,basePath):
		self.basePath=basePath
		self.curPath=None

	#-------------------------------------------------------------------------
	#Show version:
	def showVersion(self):
		print("AIChatSession 0.02");

	#-------------------------------------------------------------------------
	#Load agent from file:
	async def loadAgent(self,path):
		agent=None
		agentDict=self.agentDict
		if(not path.startswith("/")):
			path=pathLib.join(self.basePath,path)
			path=pathLib.abspath(path)
		if(path in agentDict):
			agent=agentDict[path];
		if(agent):
			return agent;
		try:
			module=import_module_from_file(path)
			agent = getattr(module, "default")
			self.agentDict[path]=agent;
			return agent
		except Exception as e:
			print(f"Failed to load agent from {path}: {e}")
			raise e
			return None

	async def runSeg(self,segVO):
		result=None
		catchSeg=None
		input=""
		if("input" in segVO):
			input=segVO["input"]
		elif("result" in segVO):
			input=segVO["result"]
		seg=segVO["seg"]
		if("catchSeg" in segVO):
			catchSeg=segVO["catchSeg"]
		try:
			while(seg):
				result=await seg["exec"](input)
				if("seg" in result):
					seg=result["seg"] 
				else:
					seg=None
				if("result" in result):
					input=result["result"]
				if(seg and ("catchSeg" in result)):
					return await self.runSeg(result);
		except Exception as e:
			print(f"Catched error: {e}")
			if(catchSeg):
				catchSegVO={"input":e,"seg":catchSeg}
				result=await self.runSeg(catchSegVO)
			else:
				raise e
		return result
			
	#-------------------------------------------------------------------------
	#Execute an agent:
	async def execAgent(self,agentPath,input):
		entry=None
		agent=None
		if(callable(agentPath)):
			agent=agentPath
		else:
			agent=await self.loadAgent(agentPath)
		agent=await agent(self)
		entry=await agent["execChat"](input)
		result=await self.runSeg(entry)
		return result
	
	#-------------------------------------------------------------------------
	#Excute an agent-seg-flow:
	async def execAISeg(self,agent,seg,input):
		execVO={"seg":seg,"input":input}
		return await self.runSeg(execVO)
	
	#-------------------------------------------------------------------------
	#APIs for agent to call:
	#-------------------------------------------------------------------------
	#import file:
	async def importFile(self,path):
		return import_module_from_file(path)
	
	#-------------------------------------------------------------------------
	async def loadAPIFromFile(self,path):
		module,apis=None,None
		if(not path.startswith("/")):
			path=pathLib.join(self.basePath,path)
			path=pathLib.abspath(path)
		try:
			module=import_module_from_file(path)
			apis = getattr(module, "ChatAPI")
			return apis
		except Exception as e:
			print(f"Failed to load agent from {path}: {e}")
			return None

	#-------------------------------------------------------------------------
	#load APIs
	async def loadAISegAPIs(self,list):
		path,i,n,sub=None,None,None,None
		allApis=[]
		n=len(list)
		for i in range(n):
			path=list[i]
			print("---loadAPI: "+path)
			sub=await self.loadAPIFromFile(path)
			if(sub):
				allApis+=sub
		return allApis
	
	#-------------------------------------------------------------------------
	async def readFile(self,path,outputFormat):
		if(not path.startswith("/")):
			path=pathLib.join(self.basePath,path)
			path=pathLib.abspath(path)
		file = open(path,"rb")
		content= file.read()
		file.close()
		if(outputFormat=="text"):
			return content.decode("utf-8")
		return content		

	#-------------------------------------------------------------------------
	async def writeFile(self,path,cotent,outputFormat):
		if(not path.startswith("/")):
			path=pathLib.join(self.basePath,path)
			path=pathLib.abspath(path)
		if(outputFormat=="text"):
			file = open(path,"w",encoding='utf-8')
		else:
			file = open(path,"wb")
		content= file.write(cotent)
		file.close()

	#-------------------------------------------------------------------------
	#output text/image to user
	async def addChatText(self,role,content,opts):
		print(f"[{role}]: {content}");
		if(opts):
			if("image" in opts):
				dataURL=opts["image"]
				image_data = dataURL.split(",")[1]
				# 将base64编码的图像数据解码
				image_bytes = base64.b64decode(image_data)
				# 将图像数据转换为PIL Image对象
				image = Image.open(BytesIO(image_bytes))
				# 显示图片
				image.show()
			if("audio" in opts):
				tempPath=pathLib.abspath(pathLib.join(self.basePath,"_temp_audio.mp3"))
				mp3_data=base64.b64decode(opts["audio"])
				file=open(tempPath,"wb")
				file.write(mp3_data)
				file.close()
				try:
					playsound(tempPath)
					os.remove(tempPath)
				except Exception as e:
					print(f"Error in playsound: {e}")
					print(f"The temp audio file is: {tempPath}")
	
	#-------------------------------------------------------------------------
	async def resizeImage(self,data_url,maxSize,imgFormat):
		image=None
		orgW,orgH=None,None
		newW,newH=None,None
		# 从dataURL中提取图片数据
		image_data = base64.b64decode(data_url.split(',')[1])

		# 使用Pillow打开图片
		image = Image.open(BytesIO(image_data))

		# 原始尺寸
		orgW,orgH=image.size
		newW=orgW
		newH=orgH
		if(orgW<=maxSize and orgH<=maxSize):
			return data_url
		if(orgW>maxSize):
			newH=int(orgH*maxSize/orgW)
			newW=maxSize
		if(newH>maxSize):
			newW=int(newW*maxSize/newH)
			newH=maxSize
		# 缩放图片
		resized_image = image.resize((newW, newH))
		# 将缩放后的图片转换为dataURL
		image_buffer = BytesIO()
		resized_image.save(image_buffer, format=(imgFormat or 'JPEG'))
		image_data = image_buffer.getvalue()
		image_base64 = base64.b64encode(image_data).decode()
		if(imgFormat=="PNG"):
			data_url_resized = f"data:image/png;base64,{image_base64}"
		else:
			data_url_resized = f"data:image/jpeg;base64,{image_base64}"
		return data_url_resized
		
	#-------------------------------------------------------------------------
	#input from user
	async def askChatInput(self,vo):
		if("prompt" in vo):
			prompt=vo["prompt"] or "Please input: ";
		else:
			prompt="Please input: ";
		return input(prompt);
	
	#-------------------------------------------------------------------------
	#Call LLM:
	async def callSegLLM(self,codeURL,opts,messages,fromSeg):
		platform,model,completion=None,None,None
		apiHash=None
		model2Platform={
			"gpt-3.5-turbo":"OpenAI",
			"gpt-3.5-turbo-16k":"OpenAI",
			"gpt-3.5-turbo-1106":"OpenAI",
			"gpt-4":"OpenAI",
			"gpt-4-32k":"OpenAI",
			"gpt-4-1106-preview":"OpenAI",
		}
		if("model" in opts):
			model=opts["model"]
		elif("mode" in opts):
			model=opts["mode"]
		else:
			model="gpt-3.5-turbo"
		platform=model2Platform.get(model, "OpenAI")
		if(platform=="OpenAI"):
			temperature=opts["temperature"] or 1;
			#Add function/tool support:
			if("apis" in opts):
				apis=opts["apis"]
				apiHash={}
				if("parallelFunction" in opts and opts["parallelFunction"]):
					stub=None
					tools=[];
					for stub in apis:
						print(stub)
						toolDef=stub["def"]							 
						tools.append({
							"type":"function",
							"function":toolDef
						})
						apiHash[toolDef["name"]]=stub
					completion = openAI.chat.completions.create(
						model=model,
						temperature=temperature,
						messages=messages,
						tools=tools,
						tool_choice="auto"
					)
				else:
					stub=None
					apiList=[];
					for stub in apis:
						toolDef=stub["def"]									 
						apiList.append(toolDef)
						apiHash[toolDef["name"]]=stub
					completion = openAI.chat.completions.create(
						model=model,
						temperature=temperature,
						messages=messages,
						functions=apiList,
						function_call="auto"
					)
			else:
				completion = openAI.chat.completions.create(
					model=model,
					temperature=temperature,
					messages=messages
				)
			result=completion.choices[0].message
			#print("Chat result:")
			#print(result)
			if(result.tool_calls):
				toolCalls=result.tool_calls
				#print("Will call tools")
				#print(toolCalls)
				messages=messages[:]
				messages.append(result)
				for toolCall in toolCalls:
					callStub=toolCall.function
					callName=callStub.name
					apiStub=apiHash[callName]
					apiFunc=apiStub["func"]
					callArgs=json.loads(callStub.arguments)
					carrArgs["session"]=self
					callResult=await apiFunc(**callArgs)
					#print(f"Call {callName} result:")
					#print(callResult)
					messages.append({
						"tool_call_id": toolCall.id,
						"role": "tool",
						"name": callName,
						"content": callResult,
					})
				return await self.callSegLLM(codeURL,opts,messages,False)
			if(result.function_call):
				functionCall=result.function_call
				#print("Will call function")
				#print(functionCall)
				messages=messages[:]
				messages.append({"role":"assistant","content":"","function_call":functionCall})
				callName=functionCall.name
				apiStub=apiHash[callName]
				apiFunc=apiStub["func"]
				callArgs=json.loads(functionCall.arguments)
				callArgs["session"]=self
				callResult=await apiFunc(**callArgs)
				#print(f"Call {callName} result:")
				#print(callResult)
				messages.append({
					"role":"function","name":callName,"content":callResult
				});
				return await self.callSegLLM(codeURL,opts,messages,False)
			return result.content
		else:
			raise Exception(f"Unknown platform: {platform}, model: {model}");

	#-------------------------------------------------------------------------
	#Call AI to draw something:
	async def callAIDraw(self,vo):
		platform,model,prompt,size,response=None,None,None,None,None
		img=None
		model2Platform={
			"dall-e-3":"OpenAI",
			"dall-e-2":"OpenAI",
		}
		if("model" in vo):
			model=vo["model"]
		elif("mode" in vo):
			model=vo["mode"]
		else:
			model="dall-e-3"
		platform=model2Platform.get(model, "OpenAI")
		if(platform=="OpenAI"):
			prompt=vo["prompt"]
			size=vo["size"]
			response=openAI.images.generate(
				model=model,
				prompt=prompt,
				n=1,
				size=size,
				response_format="b64_json"
			)
			img = response.data[0].b64_json;
			return {"code":200,"img":img}
		else:
			return {"code":400,"info":f"Unknown model: {model}"}
	
	def genMp3Name(self):
		now = datetime.now()
		now=now.strftime("%Y_%m_%d_%H_%M_%S")
		return "speech"+now+".mp3"
	#-------------------------------------------------------------------------
	async def callAITTS(self,vo):
		platform,model,input,voice,response=None,None,None,None,None
		file=None
		content=None
		tempPath=pathLib.abspath(pathLib.join(self.basePath,self.genMp3Name()))
		img=None
		model2Platform={
			"tts-1":"OpenAI",
			"tts-1-hd":"OpenAI",
		}
		if("model" in vo):
			model=vo["model"]
		elif("mode" in vo):
			model=vo["mode"]
		else:
			model="tts-1"
		platform=model2Platform.get(model, "OpenAI")
		if(platform=="OpenAI"):
			input=vo["input"]
			voice=vo["voice"]
			response=openAI.audio.speech.create(
				model=model,
				input=input,
				voice=voice
			)
			response.stream_to_file(tempPath)
			file = open(tempPath,"rb")
			content= file.read()
			file.close()
			content=base64.b64encode(content).decode()
			print("TTS output into:"+tempPath)
			return {"code":200,"mp3":content}
		return {"code":400,"info":f"Unknown model: {model}"}
		
	#-------------------------------------------------------------------------
	async def pipeChat(self,path,input,hideInter):
		return await self.execAgent(path,input)
	
	#-------------------------------------------------------------------------
	async def webCall(self,vo,fromAgent,timeout):
		response=None
		url=vo.url
		method=vo["method"] if("method" in vo) else "GET"
		headers=vo["headers"] if("headers" in vo) else {}
		argMode=vo["argMode"] if("argMode" in vo) else None
		
		if(argMode=="JSON"):
			headers["Content-Type"]="application/json";
			with httpx.Client() as client:
				response = client.request(method, url, headers=headers, json=vo["json"])
		elif(argMode=="TEXT"):
			headers["Content-Type"]="text/plain";
			with httpx.Client() as client:
				response = client.request(method, url, headers=headers, data=vo["text"])
		elif(argMode=="DATA"):
			headers["Content-Type"]="application/octet-stream";
			with httpx.Client() as client:
				response = client.request(method, url, headers=headers, data=vo["data"])
		else:
			with httpx.Client() as client:
				response = client.request(method, url, headers=headers)
		if response.status_code == httpx.codes.OK:
			return {"code":200,"data":response.text}
		else:
			return {"code":response.status_code,"info":response.text}
	
	#-------------------------------------------------------------------------
	#Show command line menu and get select:
	def showMenu(self,prompt, items):
		idx=None
		print(prompt)
		n=len(items)
		for i in range(n):
			print(f"[{i+1}]: ")
			print("    "+items[i]["text"])
		while(True):
			idx=input("Input a index of your choice: ")
			try:
				idx=int(idx)
			except Exception as e:
				idx=-1;
			idx=idx-1
			if idx>=0 and idx<n:
				break;
		return items[idx]
				
	#-------------------------------------------------------------------------
	#Show confrim buttons, menu...
	async def askUserRaw(self,vo):
		askType,item,items=None,None,None
		askType=vo["type"]
		#--Button confirm:
		if(askType=="confirm"):
			items=[]
			if(vo["button1"]):
				items.append({text:vo["button1"],code:1})
			else:
				items.append({text:"OK",code:1})
			if(vo["button2"]):
				items.append({text:vo["button2"],code:0})
			else:
				items.append({text:"Cancel",code:0})
			if(vo["button3"]):
				items.append({text:vo["button3"],code:2})
			item=self.showMenu(vo["prompt"],items)
			return [item["text"],item["code"]]
		#--Menu selections:
		if(askType=="menu"):
			items=vo["items"]
			item=self.showMenu(vo["prompt"],items)
			return [item["text"],item]
		#--Input:
		if(askType=="input"):
			path=""
			inputPath=""
			#--File:
			if("path" in vo):
				if("prompt" in vo):
					prompt=vo["prompt"] or "Please input: "
				else:
					prompt="Please input: "
				inputPath=path=input(prompt)
				if(not path.startswith("/")):
					path=pathLib.join(self.basePath,path)
					path=pathLib.abspath(path)
				return [inputPath,path]				
		
#Exports:
__all__ = ["AISession"]



