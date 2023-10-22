import requests
import base64
import os
from dotenv import load_dotenv
load_dotenv()

appId = os.getenv('APPID')
accessKey = os.getenv('ACCESSKEY')
accessSecret = os.getenv('ACCESSSECRET')
projectId = os.getenv('PROJECTID')
channel = "SMS"
identity = "+918840194848"
url = "https://us.conversation.api.sinch.com/v1/projects/" + projectId + "/messages:send"

data = accessKey + ":" + accessSecret
encodedBytes = base64.b64encode(data.encode("utf-8"))
accessToken = str(encodedBytes, "utf-8")

payload = {
  "app_id": appId,
  "recipient": {
      "identified_by": {
          "channel_identities": [
            {
                "channel": channel,
                "identity": identity
            }  
            ]
      }
  },
  "message": {
      "text_message": {
          "text": "Dear user, our model have detected some malicious traffic on your network which could be a possible attempt of a DDOS attack. You can perform the following action :\n \n 1.Disconnect all your devices from the network.\n 2.Check if any unknown software is installed on your device. \n 3.Contact a security personnel ASAP. \n  \nHope you find this alert helpful and took the action at right time."
      }
  }  
}

headers = {
  "Content-Type": "application/json",
  "Authorization": "Basic " + accessToken
}

response = requests.post(url, json=payload, headers=headers)

data = response.json()
print(data)