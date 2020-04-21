import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put


class ISClient:
    def __init__(self, url):
        self.url = url
        self.get_token()

    def get_token(self):
        request = post(
            url="{url}/api/login".format(url=self.url),
            auth=HTTPBasicAuth('admin', ')m$`mMcd)!u(!X"/'),
        )

        print(json.loads(request.content))
        token = json.loads(request.content)["token"]
        self.token = token
        self.headers = {
            "Authorization": "Bearer " + token,
        }

    def send_image(self, path2img):
        try:
            with open(path2img, 'rb') as img:
                request = post(
                    url="{url}/api/".format(url=self.url),
                    files={
                        'image': img
                    },
                    headers=self.headers
                )
            return json.loads(request.content)["image_id"]
        except Exception as e:
            print("Image sending error: {}".format(str(e)))
            return None
