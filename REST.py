import boto3
import json
from flask import Flask, jsonify, request
app = Flask(__name__) #might change the name later, if needed

client = boto3.client("lambda")

#section dedicated to storing data
jobs = {} #{jid:job}
users = {} #{uid: [jid,jid,jid]}
jobId = 0

@app.route('/')
@app.route('/jobs')
def getAllJobs():

	ret = []
	for key in jobs.keys():
		job = jobs[key]
		ret.append({'job_id':job['id'],'uid':job['user'],'status':job['status'],'result':job['response']})
	
	return json.dumps(ret)
    #return (response)
	#print(ret)
	#print(type(ret))
	#return (ret)
    
    
@app.route('/jobs/', methods = ['POST'])#request = {"uid": string, "code": string, "input": {}}
def createJob():
	global jobs, users, jobId
	print("request:\n" + str(request.data))
	if request.is_json:
		#update jobId as fast as possible
		myId = jobId
		jobId += 1

		#handle post params
		reqJson = request.get_json()
		uid = str(reqJson['uid'])
		code = str(reqJson['code'])
		inp = str(reqJson['input']) #inp is a JSON string

		#handle data management
		if uid in users.keys():
			users[uid].append(myId)
		else:
			users[uid] = [myId]
		jobs[myId] = {'id':myId,'code':code,'input':inp, 'user':uid, 'status':'RUNNING', 'response':''}

		#handle Lambda Invoke
		response = client.invoke(
			FunctionName='Jobs',
			InvocationType='RequestResponse', #try using Event for async call
			Payload=bytes(json.dumps({"input": inp, "code": code}), "utf-8")
		)
		load = json.loads(response["Payload"].read())

		#verify if the job was not deleted
		if(not(myId in jobs.keys())):
			return json.dumps({"response": 1, "message":"The task was deleted before it finish running"}) #error

		#check for timeout or another Lambda Error
		if("errorMessage" in load.keys()):
			jobs[myId]['status'] = 'ERROR'
			if("Task timed out after" in load['errorMessage']):
				jobs[myId]['response'] = "Task timed out"
			else:
				jobs[myId]['response'] = load['errorMessage']
			return json.dumps({"job_id":myId})


		#handle result
		jobs[myId]['response'] = load['stdout']

		if(load['success'] == 0):
			jobs[myId]['status'] = 'DONE'
		else:
			jobs[myId]['status'] = 'ERROR'

		#return job id as requested by the project
		return json.dumps({"job_id":myId})

	#request is not a json	
	return json.dumps({"response": 1, "message":"The payload received was not a JSON object"}) #error

@app.route('/jobs/run/<int:job_id>', methods = ['POST'])#request = 
def executeJob(job_id):
	if request.is_json:
		global jobs
		#update jobId as fast as possible
		myId = job_id

		#handle post params
		job = jobs[job_id]
		print(json.dumps(job))
		uid = job['id']
		code = job['code']

		inp = request.get_json() #inp is a JSON request


		jobs[myId]['response'] = ''
		jobs[myId]['status'] = 'RUNNING'

		#handle Lambda Invoke
		response = client.invoke(
			FunctionName='Jobs',
			InvocationType='RequestResponse', #try using Event for async call
			Payload=bytes(json.dumps({"input": json.dumps(inp), "code": code}), "utf-8")
		)
		load = json.loads(response["Payload"].read())
		#print(load)

		#verify if the job was not deleted
		if(not(myId in jobs.keys())):
			return json.dumps({"response": 1, "message":"The task was deleted before it finish running"}) #error

		#check for timeout or another Lambda Error
		if("errorMessage" in load.keys()):
			jobs[myId]['status'] = 'ERROR'
			if("Task timed out after" in load['errorMessage']):
				jobs[myId]['response'] = "Task timed out"
			else:
				jobs[myId]['response'] = load['errorMessage']
			return json.dumps({"job_id":myId})


		#handle result
		jobs[myId]['response'] = load['stdout']

		if(load['success'] == 0):
			jobs[myId]['status'] = 'DONE'
		else:
			jobs[myId]['status'] = 'ERROR'


		return json.dumps({"job_id":myId})
	
	#request is not a json	
	return json.dumps({"response": 1, "message":"The payload received was not a JSON object"}) #error

@app.route('/jobs/delete/<int:job_id>',methods = ['POST'])
def deleteJob(job_id):

	global jobs, users

	if(not (job_id in jobs.keys())):
		return json.dumps({"response": 1}) #error

	job = jobs[job_id]
	userId = job['user']

	jobs.pop(job_id, None)
	users[userId].remove(job_id)
	
	return json.dumps({"response": 0}) #success

@app.route('/jobs/new/',methods = ['POST'])
def newJob():
	global jobs, users, jobId
	print("request:\n" + str(request.data))
	if request.is_json:
		#update jobId as fast as possible
		myId = jobId
		jobId += 1

		#handle post params
		reqJson = request.get_json()
		uid = str(reqJson['uid'])
		code = str(reqJson['code'])
		inp = str(reqJson['input']) #inp is a JSON string

		#handle data management
		if uid in users.keys():
			users[uid].append(myId)
		else:
			users[uid] = [myId]

		jobs[myId] = {'id':myId,'code':code,'input':inp, 'user':uid, 'status':'WAITING', 'response':''}

		#return job id as requested by the project
		return json.dumps({"job_id":myId})

	#request is not a json	
	return json.dumps({"response": 1, "message":"The payload received was not a JSON object"}) #error

@app.route('/jobs/<int:job_id>',methods = ['GET'])
def getJob(job_id):

	if(not job_id in jobs.keys()):
		return "0"

	job = jobs[job_id]
	ret = {'job_id':job['id'],'uid':job['user'],'status':job['status'],'result':job['response']}
	
	return json.dumps(ret)

@app.route('/jobs/input/<int:job_id>',methods = ['GET'])
def getJobInput(job_id):

	if(not job_id in jobs.keys()):
		return "0"

	job = jobs[job_id]
	#ret = {'job_id':job['id'],'uid':job['user'],'status':job['status'],'result':job['response']}
	
	return json.dumps(job['input'])

@app.route('/jobs/code/<int:job_id>',methods = ['GET'])
def getJobCode(job_id):

	if(not job_id in jobs.keys()):
		return "0"

	job = jobs[job_id]

	return json.dumps(job['code'])

@app.route('/user/<uid>',methods = ['GET'])
def getUserJobs(uid):

	ret = []
	if(not uid in users.keys()):
		return json.dumps(ret)

	for job_id in users[uid]: 
		job = jobs[job_id]
		ret.append( {'job_id':job['id'],'uid':job['user'],'status':job['status'],'result':job['response']} )
	
	return json.dumps(ret)

if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True, port=5000)