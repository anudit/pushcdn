from pushbullet import PushBullet
import json
import os
from dotenv import load_dotenv
load_dotenv()

APIKEY = os.environ.get("APIKEY")
CHANNEL = os.environ.get("CHANNEL")
print(CHANNEL)
p = PushBullet(APIKEY)

def getPushUrl(file_address = None):
    if (os.path.isfile(file_address) == False):
        raise ValueError("invalid path")

    activeSubs = p.active(p.getSubscriptions())
    checkCDN = [x for x in activeSubs if (x['channel']['tag'] == CHANNEL)]
    channelID = checkCDN[0]['channel']['iden']
    if (checkCDN):
        p.pushFile(CHANNEL, os.path.basename(file_address), os.path.splitext(file_address)[0], open(file_address, "rb"), recipient_type = "channel_tag")
        chats = p.getPushHistory();
        for x in chats:
            if ('channel_iden' in x and 'file_url' in x):
                    if (x['channel_iden'] == channelID):
                        return x['file_url']
    else:
        raise Exception("No Channel Setup")

print(getPushUrl("link.png"))