from slackclient import SlackClient
import os

class NOTIF:
    def __init__(self, skey):
        self.slack_token = skey
        self.sc = SlackClient(self.slack_token)

    def post(self, topost, aptlink):
        texttopost = ""
        for key, value in topost.items():
            if key != 'imagelink':
                texttopost += '*' + str(key) + '*: ' + str(value) + "\n"
        texttopost += '*link*: ' + aptlink

        self.sc.api_call(
          "chat.postMessage",
          channel="#bot",
          text=texttopost,
          attachments=[
            {
                "image_url": topost['imagelink']
            }
          ]
        )
