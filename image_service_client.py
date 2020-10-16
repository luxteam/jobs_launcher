import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put
from requests.exceptions import RequestException
from core.config import main_logger, MAX_UMS_SEND_RETRIES
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
        send_try = 0
        while send_try < MAX_UMS_SEND_RETRIES:
            try:
                main_logger.info("Try to send picture {} to Image Service (try #{})".format(path2img, send_try))
                with open(path2img, 'rb') as img:
                    response = post(
                        url="{url}/api/".format(url=self.url),
                        files={
                            'image': img
                        },
                        headers=self.headers
                    )
                    img.close()
                main_logger.info('Image sent with code {} (try #{})'.format(response.status_code, send_try))
                image_id = json.loads(response.content.decode("utf-8"))["image_id"]
                main_logger.info("Image sent. Got an image_id: {} (try #{})".format(image_id, send_try))
                return image_id
            except Exception as e:
                main_logger.error("Image sending error: {} (try #{})".format(str(e), send_try))
            send_try += 1
        else:
            return -1
