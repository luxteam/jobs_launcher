import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put
import logging

logging.basicConfig(filename='rbs.log',level=logging.DEBUG)
logger = logging.getLogger("rbs")


class RBS_Client:
    def __init__(
        self,
        build_id,
        suite_id,
        job_id,
        url,
        env_label
    ):
        # TODO: in thread loading schema from api
        self.job_id = job_id
        self.url = url
        self.build_id = build_id
        self.env_label = env_label
        self.suite_id = suite_id
        self.headers = None
        self.token = None

        # auth
        try:
            self.get_token()
        except Exception as e:
            logger.error(str(e))

    def get_token(self):
        try:
            response = post(
                url="{url}/user/login".format(url=self.url),
                auth=HTTPBasicAuth('dm1tryG', 'root'),
            )

            token = json.loads(response.content)["token"]
            self.token = token
            self.headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }

            logger.info("Auth token")
        except Exception as e:
            logger.error(str(e))


    def get_suite_id_by_name(suite_name):
        try:
            response = get(url="{url}/api/build?id={build_id}&jobId={job_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    job_id=self.job_id
                )
            )

            suites = [el['suite'] for el in json.loads(response.content)['suites'] if el['suite']['name'] == suite_name]
            self.suite_id = suites[0]['_id']
            logger.info(f"Get suite id by name {suite_name}")

        except Exception as e:
            self.suite_id = None
            logger.error(str(e))



    def send_test_suite(self, res, env):
        try:
            data = {
                "test_cases_results": res,
                "environment": env,
                "env_label": self.env_label
            }
            response = post(
                headers=self.headers,
                data=json.dumps(data),
                url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    suite_id=self.suite_id,
                    job_id=self.job_id
                )
            )
            logger.info(response.content)
            logger.info('Test suite result sent.')

            return response

        except Exception as e:
            logger.error(str(e))

    def define_environment(self, env):
        try:
            data = {
                "env_label": self.env_label,
                "environment": env
            }
            response = put(
                headers=self.headers,
                data=json.dumps(data),
                url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    suite_id=self.suite_id,
                    job_id=self.job_id
                )
            )
            logger.info("Environment defined")
            return response

        except Exception as e:
            logger.error(str(e))
