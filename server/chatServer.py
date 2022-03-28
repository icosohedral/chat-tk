from django.shortcuts import render
import requests, json, time, os

def chat(request):
    result = {}
    if request.method=='GET':
        handshake = request.GET.get('handshake',default='') # for handshake
        timestamp = request.GET.get('timestamp',default='') # for timestamp
        username = request.GET.get('username',default='') # for username
        message = request.GET.get('message',default='') # for message
        getmessage = request.GET.get('getmessage',default='') # for getmessage
    if handshake:
        result = {'text': 'alive'}
        return render(request, 'api.html', result)
    elif timestamp and username and message:
        if chatSave(timestamp, username, message):
            result = {'text': 'succ'}
        else:
            result = {'text': 'err'}
        return render(request, 'api.html', result)
    elif getmessage: 
        timestamp = float(getmessage)
        newMessages = getNewMessages(timestamp)
        result = {'text': newMessages}
        return render(request, 'api.html', result)
    else:
        result = {'text': 'invalid request'}
        return render(request, 'api.html', result)
        
def chatSave(timestamp, username, message):
    path = "/root/web/web/static/res/chat/"
    if 'message.json' in os.listdir(path):
        with open(path+'message.json', 'r') as file:
            content = file.read()
        messageJS = json.loads(content)
    else:
        messageJS = {"messages":[]}
    newMessage = {"timestamp":timestamp, "username":username, "message":message}
    messageJS["messages"].append(newMessage)
    with open(path+'message.json', 'w') as file:
        file.write(json.dumps(messageJS))
    return True
    
def getNewMessages(timestamp):
    messages, result = [], {}
    path = "/root/web/web/static/res/chat/"
    with open(path+'message.json', 'r') as file:
        content = file.read()
    messageJS = json.loads(content)
    for message in  messageJS["messages"]:
        if float(message["timestamp"]) > timestamp:
            messages.append(message)
    result["messages"] = messages
    return result
    