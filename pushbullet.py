import json
import requests
from requests.auth import HTTPBasicAuth
from websocket import create_connection

HOST = "https://api.pushbullet.com/v2"

class PushBullet():
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _request(self, method, url, postdata=None, params=None, files=None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "User-Agent": "pushCDN"}

        if postdata:
            postdata = json.dumps(postdata)

        r = requests.request(method,
                             url,
                             data=postdata,
                             params=params,
                             headers=headers,
                             files=files,
                             auth=HTTPBasicAuth(self.apiKey, ""))

        r.raise_for_status()
        return r.json()

    def addDevice(self, device_name):
        data = {"nickname": device_name,
                "type": "stream"
                }
        return self._request("POST", HOST + "/devices", data)

    def getDevices(self):
        return self._request("GET", HOST + "/devices")["devices"]

    def deleteDevice(self, device_iden):
        return self._request("DELETE", HOST + "/devices/" + device_iden)

    def pushNote(self, recipient, title, body, recipient_type="device_iden"):
        data = {"type": "note",
                "title": title,
                "body": body}

        data[recipient_type] = recipient

        return self._request("POST", HOST + "/pushes", data)

    def pushAddress(self, recipient, name, address, recipient_type="device_iden"):
        data = {"type": "address",
                "name": name,
                "address": address}
				
        data[recipient_type] = recipient
				
        return self._request("POST", HOST + "/pushes", data)

    def pushList(self, recipient, title, items, recipient_type="device_iden"):
        data = {"type": "list",
                "title": title,
                "items": items}
				
        data[recipient_type] = recipient

        return self._request("POST", HOST + "/pushes", data)

    def pushLink(self, recipient, title, url, recipient_type="device_iden"):
        data = {"type": "link",
                "title": title,
                "url": url}
				
        data[recipient_type] = recipient
				
        return self._request("POST", HOST + "/pushes", data)

    def pushFile(self, recipient, file_name, body, file, file_type=None, recipient_type="device_iden"):
        if not file_type:
            try:
                import magic
            except ImportError:
                raise Exception("No file_type given and python-magic isn't installed")
            if hasattr(magic, "from_buffer"):
                file_type = magic.from_buffer(file.read(1024))
            else:
                _magic = magic.open(magic.MIME_TYPE)
                _magic.compile(None)

                file_type = _magic.file(file_name)

                _magic.close()

            file.seek(0)

        data = {"file_name": file_name,
                "file_type": file_type}

        upload_request = self._request("GET",
                                       HOST + "/upload-request",
                                       None,
                                       data)

        upload = requests.post(upload_request["upload_url"],
                               data=upload_request["data"],
                               files={"file": file},
                               headers={"User-Agent": "pyPushBullet"})

        upload.raise_for_status()

        data = {"type": "file",
                "file_name": file_name,
                "file_type": file_type,
                "file_url": upload_request["file_url"],
                "body": body}
				
        data[recipient_type] = recipient

        return self._request("POST", HOST + "/pushes", data)

    def getPushHistory(self, modified_after=0, cursor=None):
        data = {"modified_after": modified_after}
        if cursor:
            data["cursor"] = cursor
        return self._request("GET", HOST + "/pushes", None, data)["pushes"]

    def deletePush(self, push_iden):
        return self._request("DELETE", HOST + "/pushes/" + push_iden)

    def getContacts(self):
        return self._request("GET", HOST + "/contacts")["contacts"]

    def deleteContact(self, contact_iden):
        return self._request("DELETE", HOST + "/contacts/" + contact_iden)

    def getUser(self):
        return self._request("GET", HOST + "/users/me")

    def getSubscriptions(self):
        return self._request("GET", HOST + "/subscriptions")['subscriptions']

    def createSubscription(self, name):
        data = {"channel_tag" : name}
        return self._request("POST", HOST + "/subscriptions", data)

    def dismissEphemeral(self, notification_id, notification_tag, package_name, source_user_iden):
        data = {"push": {"notification_id": notification_id,
                         "notification_tag": notification_tag,
                         "package_name": package_name,
                         "source_user_iden": source_user_iden,
                         "type": "dismissal"},
                "type": "push"}

        return self._request("POST", HOST + "/ephemerals", data)

    def active(self, l):
        return [x for x in l if x['active'] == True]

    def realtime(self, callback):
        url = "wss://stream.pushbullet.com/websocket/" + self.apiKey
        ws = create_connection(url)
        while 1:
            data = ws.recv()
            data = json.loads(data)
            if data["type"] != "nop":
                callback(data)