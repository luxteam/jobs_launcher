import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put
from requests.exceptions import RequestException
from core.config import main_logger
import traceback


class ISClient:
    def __init__(self, url, login, password):
        self.url = url
        self.login = login
        self.password = password
        self.get_token()

    def get_token(self):
        response = post(
            url="{url}/api/login".format(url=self.url),
            auth=HTTPBasicAuth(self.login, self.password),
        )
        if response.status_code == 404:
            raise RequestException("Cant connect image service. Check url")
        content = response.content.decode("utf-8")
        if 'error' in content:
            raise RequestException('Check login and password')
        token = json.loads(content)["token"]
        self.token = token
        self.headers = {
            "Authorization": "Bearer " + token,
        }

    def send_image(self, path2img):
        try:
            main_logger.info("Try to send picture to Image Service")
            with open(path2img, 'rb') as img:
                response = post(
                    url="{url}/api/".format(url=self.url),
                    files={
                        'image': img
                    },
                    headers=self.headers
                )
                img.close()
            main_logger.info("Image sent")
            return json.loads(response.content.decode("utf-8"))["image_id"]
        except Exception as e:
            main_logger.error("Image sending error: {}".format(str(e)))
            return -1
