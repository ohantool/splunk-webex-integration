
__          ________ ____  ________   __   _____ _____  _     _    _ _   _ _  __
\ \        / /  ____|  _ \|  ____\ \ / /  / ____|  __ \| |   | |  | | \ | | |/ /
 \ \  /\  / /| |__  | |_) | |__   \ V /  | (___ | |__) | |   | |  | |  \| | ' /
  \ \/  \/ / |  __| |  _ <|  __|   > <    \___ \|  ___/| |   | |  | | . ` |  <  
   \  /\  /  | |____| |_) | |____ / . \   ____) | |    | |___| |__| | |\  | . \
    \/  \/   |______|____/|______/_/ \_\ |_____/|_|    |______\____/|_| \_|_|\_\
contact me if you have any questions https://www.linkedin.com/in/ohantool


Make sure to have Python 3 installed.
credit for oauth2 utility functions code https://github.com/WebexSamples/webex-flask-oauth-example

- Fill in your Workspace IDs in the oauth2.py file. Please read about it here https://developer.webex.com/docs/api/v1/workspaces
- Replace the required variables (Client ID, Secrect ID etc...) in the oauth2.py file
- Replace the URL in the <a> tag in index.html
- Replace HEC token Details and and your splunk URL in the oauth2.py file

Read how to setup HEC here: https://docs.splunk.com/Documentation/Splunk/9.4.0/Data/UsetheHTTPEventCollector

To run the server application, open a command terminal, and navigate to the folder where you saved this Python script.

*python3 oauth2.py*

You should see this in the terminal:

Listening on http://0.0.0.0:10060...

copy and paste above URL into browser and follow the prompts

After the authentication is done the app schedules calling the Webex APIs and sends them to Splunk HEC every hour

**Note**: Your Redirect_URI in the Integration's settings on Developer Webex site should be: http://0.0.0.0:10060/oauth or if you're using any other hosting platform it would be https://YOUR_SERVER/oauth
