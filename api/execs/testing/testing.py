import http.client
import xmlrpc.client as cl
import api.execs.conf.conf as conf
from jsonrpcclient import request
import requests


request_url = f"https://api.telegram.org/bot{conf.Bot_Token}/sendCode?api_hash={conf.Constants['api_hash']}&" + \
          f"api_id={conf.Constants['api_id']}&phone_number=87789197489"


headers = {
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
            "Content-type": "application/json",
            "Content-Length": ""
        }


def executer():

    xml = b"auth.sendCode#a677244f " \
          b"phone_number:string " \
          b"api_id:int " \
          b"api_hash:string " \
          b"settings:CodeSettings = auth.SentCode;"

    xml = b"<?xml version='1.0'?>" \
        b"\n<methodCall>" \
            b"\n<methodName>auth.SendCode</methodName>" \
            b"\n<params>" \
                b"\n<phone_number>" \
                    b"\n<value><string>'87789197489'</string></value>" \
                b"\n</phone_number>" \
                b"\n<api_id>" \
                    b"\n<value><int>16147296</int></value>" \
                b"\n</api_id>" \
                b"\n<api_hash>" \
                    b"\n<value><string>'b37c46483b8f55c3a0221e9c3b859825'</string></value>" \
                b"\n</api_hash>" \
                b"\n</params>" \
        b"\n</methodCall>" \
    b"\n"

    headers["Content-Length"] = str(len(xml))
    connection = http.client.HTTPConnection(f"https://api.telegram.org/")
    connection.putrequest('POST', '/')
    for key, value in headers.items(): connection.putheader(key, value)
    connection.endheaders(xml)
    connection.getresponse().read()

def json_rpc():
    response = request()
    print(response)


print(request_url)

def send_js_request():
    session = requests.Session()
    method = 'net_version'
    params = []
    payload = {"jsonrpc": "2.0",
               "method": method,
               "params": params,
               "id": 1}
    response = session.post(request_url, headers=headers, json=payload)
    print(response.text)


executer()