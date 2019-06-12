import os
import json
import requests as req
from concurrent.futures import ProcessPoolExecutor
from requests_futures.sessions import FuturesSession



#config
ADDRESS = "127.0.0.1:5000"              #change this for your access point
MAX_WORKERS = 4                         #default in the futures lib is 8
WORK_TYPE = "PROCESS"                    #THREAD | PROCESS. changes what kind of parallelism is udef for async

username = "User"
url = "http://" + ADDRESS + "/"


#setup
if(WORK_TYPE == "THREAD"):
    session = FuturesSession(max_workers = MAX_WORKERS)
elif(WORK_TYPE == "PROCESS"):
    session = FuturesSession(executor=ProcessPoolExecutor(max_workers=MAX_WORKERS),
                         session=req.Session())
else:
    print("WORK_TYPE config is not set correctly!!!")
    exit()

#hooks

def dummy_hook(resp, *args, **kwargs):
    pass

def test_hook(resp, *args, **kwargs):
    print("running the hook")
    print(dir(resp))
    print(json.dumps(resp.json()))
    print(args)
    print(kwargs)


#REST access
'''
def createJob(payload):

    f1 = session.post(url + "jobs/", json=payload, hooks={'response':func_hook})
    f2 = session.post(url + "jobs/", json=payload)

    print(dir(f1))
    print(f1.running())
    \'''
    while(f1.running()):
        pass
    print('waited')
    \'''
    #print(f1.cancelled())
    #f1.cancel()
    #print(f1.running())
    #print(f1.cancelled())
    r1 = f1.result()
    #r2 = f2.result()
    print("response one status: " , r1.status_code)
    #print("response two status: " , r2.status_code)

    print("waiting for response one...")
'''
def createJob(code,inp):


    payload = {"uid":username,"code":code, "input":json.dumps(inp)}

    session.post(url + "jobs/new/", json=payload, hooks={'response':dummy_hook}) #async post


def runJob(job_id,inp):

    session.post(url + "jobs/run/" + str(job_id), json=inp, hooks={'response':dummy_hook}) #async post

def deleteJob(job_id):
    r = req.post(url + 'jobs/delete/' + str(job_id))
    #print(r.text)
    res = r.json()['response']
    return int(res)
    

def getJob(job_id):
    r = req.get(url + 'jobs/' + str(job_id))
    if(r.text == "0"):
        return 0
    return r.json()

def getJobInput(job_id):
    r = req.get(url + 'jobs/input/' + str(job_id))
    if(r.text == "0"):
        return 0
    return r.json()

def getJobCode(job_id):
    r = req.get(url + 'jobs/code/' + str(job_id))
    if(r.text == "0"):
        return 0
    return r.json()

def getMyJobs():
    r = req.get(url + 'user/' + username)
    if(r.text == '[]'):
        return 0
    return r.json()


#helpers
def printHeader():
    print('''

\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\n\n
   ___       _       _____          _               _             _             
  |_  |     | |     |  _  |        | |             | |           | |            
    | | ___ | |__   | | | |_ __ ___| |__   ___  ___| |_ _ __ __ _| |_ ___  _ __ 
    | |/ _ \| '_ \  | | | | '__/ __| '_ \ / _ \/ __| __| '__/ _` | __/ _ \| '__|
/\__/ / (_) | |_) | \ \_/ / | | (__| | | |  __/\__ \ |_| | | (_| | || (_) | |   
\____/ \___/|_.__/   \___/|_|  \___|_| |_|\___||___/\__|_|  \__,_|\__\___/|_|   
                                                            (By Jean Walper)


''')
    print('Connected to server: ', ADDRESS, '.')
    print("User: " + username + '.\n\n\n')

def formatJob(job):
    #format status
    status = job['status']
    if(status == "ERROR"):
        status = " ERROR "
    elif(status == "DONE"):
        status = " DONE  "
    #format response
    resp = job["result"].replace('\n','\\n')
    if(len(resp) > 36):
        resp = resp[:36] + "..."
    #final string
    s = " |ID - {0}| STATUS - {1}| RESULT - {2}|".format(job['job_id'],status,resp)

    return s


#States

def runJobState(job):
    inp = json.loads(getJobInput(job["job_id"]))
    code = getJobCode(job["job_id"])

    printHeader()
    print("This job code:\n")
    print(code, '\n')
    if(len(inp.keys()) > 0):
        print("job has input. Want to use default values?\n1 - yes\n2 - no")
        print(inp)
        i = int(input())
        if(i == 2):
            for k,v in inp.items():
                print("input a value for ", k ,": (default is", v, ")")
                i = input()
                inp[k] = i
            print("Done!")
    print("Confirm job Execution?\n1 - yes\n2 - no")
    i = int(input())
    if(i == 2):
        return
    runJob(job["job_id"],inp)
    print("Job request sent!!!\n\nType anything to go back!")
    input()

def deleteJobState(job):
    code = getJobCode(job["job_id"])

    printHeader()
    print("This job code:\n")
    print(code,'\n')
    print("Confirm job DELETION?\n1 - yes\n2 - no")
    i = int(input())
    if(i == 2):
        return
    print("Are You Sure? (YOU ARE DELETING THIS JOB AND IT CANT BE UNDONE)\n1 - yes\n2 - no")
    i = int(input())
    if(i == 2):
        return

    res = deleteJob(job["job_id"])
    if(res == 1):
        printError("Job could not be deleted!")
    print("Job deleted!\n\nType anything to go back!")
    input()

    

def seeMyJobs():
    while(True):
        printHeader()

        jobs = getMyJobs()
        if(jobs == 0):
            printError("No jobs for user " + username + ".")
            return
        maxLines = 12

        for job in jobs:
            if(maxLines == 0):
                print("more...")
                break
            else:
                print( formatJob(job))
                maxLines -= 1

        for i in range(maxLines):
            print(' |')
        
        
        print("1 - Back\n2 - Refresh\n3 - Run job\n4 - Delete Job\n")
        i = int(input())

        if(i == 1):
            return
        elif(i == 2):
            continue
        elif(i == 3):
            printHeader()

            maxLines = 12

            for job in jobs:
                if(maxLines == 0):
                    print("more...")
                    break
                else:
                    print(12 - maxLines, formatJob(job))
                    maxLines -= 1

            for i in range(maxLines):
                maxLines -= 1
                print('   |')
            
            print("Enum of wich job to run: (the first number before the job)\n")
            i = int(input())
            print(12 - maxLines)
            if(i >= 12 - maxLines):
                printError("No job had this enum")
                continue
            runJobState(jobs[i])

        elif(i == 4):
            printHeader()

            maxLines = 12

            for job in jobs:
                if(maxLines == 0):
                    print("more...")
                    break
                else:
                    print(12 - maxLines, formatJob(job))
                    maxLines -= 1

            for i in range(maxLines):
                print('   |')
            
            print("Enum of wich job to DELETE: (the first number before the job)\n")
            i = int(input())
            print(12 - maxLines)
            if(i >= 12 - maxLines):
                printError("No job had this enum")
                continue
            deleteJobState(jobs[i])


def createInput():
    inp = {}
    while(True):
        printHeader()
        print("Actual input:")
        print(inp)
        print("Type a input")
        name = input()
        print("Type a default value:")
        val = input()
        inp[name] = val
        print("Want to input another value?\n1 - yes\n2 - no")
        if(input() == '2'):
            return inp

def createJobState():
    while(True):
        printHeader()

        print("Type the path for the code file:\nExample: ./scripts/test.py\n(type 'back' to exit this screen. (dont call your file 'back'))")
        path = input()
        if(path == "back"):
            return
        exist = os.path.isfile(path)
        if(not exist):
            printError("Filepath doesn't exist!")
            continue
        f = open(path, "r")
        code = f.read()
        f.close()

        printHeader()
        print("Your code:")
        print(code)
        print('\n\ncontinue?\n1 - yes\n2 - no')
        i = int(input())
        if(i == 2):
            continue
        
        printHeader()
        print("Want to create a input for your code?\n1 - yes\n2 - no")
        i = int(input())
        inp = {}
        if(i == 1):
            inp = createInput()
        
        createJob(code,inp)
        printHeader()
        print("Job request sent!!!\n\n")
        print("Want to create another job?\n1 - yes\n2 - no")
        i = int(input())
        if(i == 2):
            return


def changeUser():
    global username
    printHeader()
    print("\n\n\n\n")
    print("New username")
    username = input()

def printError(error):
    printHeader()
    print("\n\n\n\n")
    print("THERE WAS AN ERROR!!!")
    print(error)
    print("\n\n")
    print("type anything to go back")
    input()

#main
#payload = {"uid":"light","code":"while(True):pass", "input":"{}"}

r = req.get(url)
print('''

\n\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\n\n\n\n
Welcome to my 
   ___       _       _____          _               _             _             
  |_  |     | |     |  _  |        | |             | |           | |            
    | | ___ | |__   | | | |_ __ ___| |__   ___  ___| |_ _ __ __ _| |_ ___  _ __ 
    | |/ _ \| '_ \  | | | | '__/ __| '_ \ / _ \/ __| __| '__/ _` | __/ _ \| '__|
/\__/ / (_) | |_) | \ \_/ / | | (__| | | |  __/\__ \ |_| | | (_| | || (_) | |   
\____/ \___/|_.__/   \___/|_|  \___|_| |_|\___||___/\__|_|  \__,_|\__\___/|_|   
                                                            (By Jean Walper)


''')
print('Connected to server: ', ADDRESS, '.\n\n')
print("Username: ")
username = input()
print('\n\nHi', username + '!\n\n')

while(True):
    printHeader()
    print('Chose a option:')
    print('\n\n')
    print('1 - See my jobs\n2 - Create new job\n8 - Change User\n9 - Exit')


    #handle input
    i = int(input())
    if(i == 1):
        seeMyJobs()
    elif(i == 2):
        createJobState()
    elif(i == 8):
        changeUser()
    elif(i == 9):
        exit()