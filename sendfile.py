from pushbullet import PushBullet
import json

APIKEY = "o.PYxIZTSjuvOEbwlAhkF4StoRc548u0cS"
CDNCHANNEL = "pushcdn"
p = PushBullet(APIKEY)
p.pushFile(CDNCHANNEL, "img.png", "File!", open("link.png", "rb"), recipient_type = "channel_tag")
print("Done!")