import os
from twilio.rest import Client
from flask import Flask
from twilio.twiml.voice_response import VoiceResponse

account_sid = 'AC5a5fac3ef5595b43b7576659dfda7cfe'
auth_token = 'f4020ccd6a768d64364d8324017c5b05'

app = Flask(__name__)

@app.route("/voice",methods=['GET','POST'])
def voice():
    resp = VoiceResponse()
    os.system('python voice_recorder.py')
    #resp.say("Hello, welcome to the st. gallen helpline")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)