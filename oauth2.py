"""
  __          ________ ____  ________   __   _____ _____  _     _    _ _   _ _  __
 \ \        / /  ____|  _ \|  ____\ \ / /  / ____|  __ \| |   | |  | | \ | | |/ /
  \ \  /\  / /| |__  | |_) | |__   \ V /  | (___ | |__) | |   | |  | |  \| | ' /
   \ \/  \/ / |  __| |  _ <|  __|   > <    \___ \|  ___/| |   | |  | | . ` |  <
    \  /\  /  | |____| |_) | |____ / . \   ____) | |    | |___| |__| | |\  | . \
     \/  \/   |______|____/|______/_/ \_\ |_____/|_|    |______\____/|_| \_|_|\_\

https://www.linkedin.com/in/ohantool
"""

# -*- coding:utf-8 -*-
import requests
import json
import os
import schedule
import time
from pyHEC import PyHEC



from flask import Flask, render_template, request, session

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)
clientID = "clientID"
secretID = "secretID"
redirectURI = "http://0.0.0.0:10060/oauth" #This could be different if you publicly expose this endpoint.

hec = PyHEC("HEC Token", "SPLUNK URL") #HEC token Details and and splunk URL

#Fill your workspace names and IDS
workSpaceIDs = [{"name":"workspace Name","id":"workSpaceID"},
{"name":"workspace Name","id":"workSpaceID"},
{"name":"workspace Name","id":"workSpaceID"}]


"""
Function Name : get_tokens
Description : This is a utility function that takes in the
              Authorization Code as a parameter. The code
              is used to make a call to the access_token end
              point on the webex api to obtain a access token
              and a refresh token that is then stored as in the
              Session for use in other parts of the app.
              NOTE: in production, auth tokens would not be stored
              in a Session. This app will request a new token each time
              it runs which will not be able to check against expired tokens.
"""
def get_tokens(code):
    print("function : get_tokens()")
    print("code:", code)
    #STEP 3 : use code in response from webex api to collect the code parameter
    #to obtain an access token or refresh token
    url = "https://webexapis.com/v1/access_token"
    headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=authorization_code&client_id={0}&client_secret={1}&"
                    "code={2}&redirect_uri={3}").format(clientID, secretID, code, redirectURI)
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)

    access_token = results["access_token"]
    refresh_token = results["refresh_token"]

    session['oauth_token'] = access_token
    session['refresh_token'] = refresh_token

    print("Token stored in session : ", session['oauth_token'])
    print("Refresh Token stored in session : ", session['refresh_token'])
    return

"""
Function Name : get_tokens_refresh()
Description : This is a utility function that leverages the refresh token
              in exchange for a fresh access_token and refresh_token
              when a 401 is received when using an invalid access_token
              while making an api_call().
              NOTE: in production, auth tokens would not be stored
              in a Session. This app will request a new token each time
              it runs which will not be able to check against expired tokens.
"""
def get_tokens_refresh():
    print("function : get_token_refresh()")

    url = "https://webexapis.com/v1/access_token"
    headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=refresh_token&client_id={0}&client_secret={1}&"
                    "refresh_token={2}").format(clientID, secretID, session['refresh_token'])
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)

    access_token = results["access_token"]
    refresh_token = results["refresh_token"]

    session['oauth_token'] = access_token
    session['refresh_token'] = refresh_token

    print("Token stored in session : ", session['oauth_token'])
    print("Refresh Token stored in session : ", session['refresh_token'])
    return

"""
Function Name : main_page
Description : when using the browser to access server at
              http://127/0.0.1:10060 this function will
              render the html file index.html. That file
              contains the button that kicks off step 1
              of the Oauth process with the click of the
              grant button
"""
@app.route("/")

def main_page():
    """Main Grant page"""
    return render_template("index.html")

"""
Function Name : oauth
Description : After the grant button is click from index.html
              and the user logs into thier Webex account, the
              are redirected here as this is the html file that
              this function renders upon successful authentication
              is granted.html. else, the user is sent back to index.html
              to try again. This function retrieves the authorization
              code and calls get_tokens() for further API calls against
              the Webex API endpoints.
"""
@app.route("/oauth") #Endpoint acting as Redirect URI.

def oauth():
    print("function : oauth()")
    """Retrieves oauth code to generate tokens for users"""
    state = request.args.get("state")
    print('state : ' + state)
    if state == '1234abcd':
        code = request.args.get("code") # STEP 2 : Capture value of the
                                        # authorization code.
        print("OAuth code:", code)
        print("OAuth state:", state)
        get_tokens(code)
        return render_template("granted.html")
    else:
        return render_template("index.html")

"""
Description : Logic of the app starts here
After Webex authentication is done the webexsplunk function will be invoked
webexsplunk() schedules calling the Webex APIs and sends them to Splunk HEC every hour
"""

@app.route("/webexsplunk")
def webexsplunk() :
    temperature()
    schedule.every().hour.do(temperature)
    while True:
        schedule.run_pending()
        print(".", end="", flush=True)
        time.sleep(1)
    return

def temperature() :
    data = workSpaceIDs
    for item in data:
        response = api_call(item["id"])
        print("status code : ", response.status_code)
            #Do a check on the response. If the access_token is invalid then use refresh
        if (response.status_code == 401) :
            get_tokens_refresh()
            response = api_call(item["id"])

        temperature = response.json()['items'][1]['mean']
        timestamp = response.json()['items'][1]['end']
        print(temperature)
        print(timestamp)
        print(item["name"])
        print("response status code : ", response.status_code)
        event = {"Workspace":item["name"], "Temperature":temperature, "TimeStamp":timestamp}
        print(hec.send(event))
    return event


def api_call(item) :
    accessToken = session['oauth_token']
    url = "https://webexapis.com/v1/workspaceMetrics?workspaceId="+item+"&metricName=temperature&aggregation=hourly"
    headers = {'accept':'application/json','Content-Type':'application/json','Authorization': 'Bearer ' + accessToken}
    response = requests.get(url=url, headers=headers)
    return response

if __name__ == '__main__':
    app.run("0.0.0.0", port=10060, debug=False)
