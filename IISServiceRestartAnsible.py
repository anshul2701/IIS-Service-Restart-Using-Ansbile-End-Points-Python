import requests
import json
import sys
import os
from atr_sdk import ATRConsul, ATRApi
import re
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import time
import argparse
import os.path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

incidentNumber = sys.argv[1]
hostName = sys.argv[2]
awxToken = sys.argv[3]
shortDescription = sys.argv[4]

print(awxToken)
atr_consul = ATRConsul()
admin_password = atr_consul.get('configuration/aaam-atr-v3-identity-management/admin.password')

atr = ATRApi('admin', admin_password)

print(hostName)
hostName = hostName+".corp.riotinto.org"
print(hostName)

if shortDescription == "IIS Service Not Running on Application Catalog Web Service Point" or shortDescription == "The IIS Admin Service (IISAdmin) isn't running.":
    serviceName = "IISService"

print(shortDescription)
print(serviceName)

templateName = "Win_IIS_Service_Restart"

api_baseurl = "https://automation.corp.riotinto.org/api/v2/"

getPayload={}
getHeaders = {
    'Authorization': 'Bearer ' + awxToken
    
}
postHeaders = {
    'Authorization': 'Bearer '+awxToken,
    'Content-Type': 'application/json'
    
}

# *****************************Start of Function****************************************

# def getAWXResourceID(resourceType, resourceName):
#     awxResourceType = resourceType
#     awxResourceName = resourceName
    
# #print("awxResourceName-------",awxResourceName)\

#     # Create the URL to get the list of resources of a type. Example list of inventories, list of job_templates, etc.\

    
#     urlNew = apiBaseURL + awxResourceType + "/"
#     print(urlNew)\
#     # GET request to collect the list of entities from AWX\

#     getResponse = requests.request("GET", urlNew, headers=getHeaders, data=getPayload, verify = False)
#     resJson = getResponse.json()
#   # print("Data coming is --",resJson)\
#   # print("awxResourceName-------",awxResourceName)\
#   # print(len(awxResourceName))\

#     # Iterate over the response of the GET request. This response contains the list of the entity type like list of inventories or list of job_templates. From the list, we need to find ID of the entity for which the name matches with awxEntityName\
#     i = 0
#     id = 0
#     resultCount=len(resJson["results"])
#     while i < resultCount:
#     #while i < resJson["count"]:
#         if resJson["results"][i]["name"] == awxResourceName:
#             id =  resJson["results"][i]["id"]
#         i += 1
#     return id
# *************End of Function********************************\

inventoryName = "Win_IIS_Service_Restart_inventory"
inventoryID = 250

invID = str(inventoryID)
# *************** Start of Function *******************************
def updateInventory(inventory):
    invUrl = api_baseurl + "inventories/" + inventory + "/hosts/" 
    
    print(invUrl)
    
    getResponse = requests.request("GET", invUrl , headers = getHeaders , data = getPayload , verify = False)
    resJson = getResponse.json()
    print(resJson)
    
   
    i = 0
    while i < resJson["count"]:
       urlDel = api_baseurl + "hosts/"+ str(resJson["results"][i]["id"]) + "/"
       getResponse = requests.request("DELETE", urlDel, headers=getHeaders, data=getPayload, verify = False)
       i += 1

# Now add the new host - call POST api for inventory with hostname to be added\
    getResponse = requests.request("GET", invUrl, headers=getHeaders, data=getPayload, verify = False)
    #postPayload = "\{\\r\\n    \"name\": \\"" +  hostName + ""\\r\\n\}"
    postPayload = json.dumps({    "name": "" +  hostName + ""})
   
    getResponse = requests.request("POST", invUrl, headers=postHeaders, data=postPayload, verify=False)
    return getResponse
# ************************* End of Function **********************


templateinventory=updateInventory(invID)

templateID = 2088
templateID = str(templateID)

def launch_template(templateid):
    templateurl = api_baseurl + "job_templates/" + templateid + "/launch/"
    
    postPayload1 = json.dumps({   "extra_vars" : {"service_name": "" + serviceName + "" }})
    print(templateurl)
    
    templatePost = requests.request("POST" , templateurl , headers = postHeaders , data = postPayload1 , verify = False)
    
    response1=json.loads(templatePost.text)
    print("response1------>>>>>",response1)
    job_id = str(response1['job'])
    timeout = time.time()+60*5
    
    while(True):
        time.sleep(4)
        jobUrl= api_baseurl + "jobs/" + job_id
        job_response= requests.get( jobUrl, headers=postHeaders, data=getPayload, verify=False)
        response2=json.loads(job_response.text)
        job_status = str(response2['status'])
        print(job_status)
        if(job_status == "new"):
            continue
        if(job_status == "pending"):
            continue
        if(job_status == "waiting"):
            continue
        if(job_status == "running"):
            continue
        if(job_status == "successful"):
            break
        if(job_status == "failed"):
            print("Job status = failed.")
            break
        if(job_status == "error"):
            print("Job status = error.")
            break
        if(job_status == "canceled"):
            print("Job status = canceled.")
            break
        if(job_response.json()['status'] == "never updated"):
            print("Job status = never updated.")
            break
    return job_status, job_id
# *************End of Function********************************\
jobtemplate= launch_template(templateID)
print("Job Status ==>",jobtemplate)
print ('#JOB_RESULT job_status=%s' %jobtemplate[0])
if str(jobtemplate =="successful"):
   job_ID1= jobtemplate[-1]
   
   print('#job_ID1=%s' %job_ID1)
   outputURL = api_baseurl + "jobs/" + job_ID1 +"/stdout/?format=txt_download"
   resJobOutput = requests.request("GET", outputURL, headers=getHeaders, data=getPayload, verify=False)
   
   print('#Job Output=%s' %resJobOutput)
   Nstr = resJobOutput.text
   lst = Nstr.split("\\n")
   print(job_ID1,lst)
   print('#JOB_RESULT data=%s' %lst)
  
else:
    result = "Not able to receive any data from the server, please check manually"
    print('#Job Output=%s' %result)
    print(" Not able to receive any data from the server, please check manually")
    


    
    






