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
        self.get_token()

    def get_token(self):
        response = post(
            url="{url}/user/login".format(url=self.url),
            auth=HTTPBasicAuth('dm1tryG', 'root'),
        )

        token = json.loads(response.content)["token"]
        self.token = token
        self.headers = {"Authorization": "Bearer " + token}

        print("Got auth token")


    def get_suite_id_by_name(self, suite_name):
        try:
            response = get(url="{url}/api/build?id={build_id}&jobId={job_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    job_id=self.job_id
                ),
                headers=self.headers
            )
            suites = [el['suite'] for el in json.loads(response.content)['suites'] if el['suite']['name'] == suite_name]
            self.suite_id = suites[0]['_id']
            print("Get suite id by name {}".format(suite_name))

        except Exception as e:
            self.suite_id = None
            print("Suite id getting error")
            print(str(e))



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
            print('Test suite result sent with code {}'.format(response.status_code))

            return response

        except Exception as e:
            print(f'Test suite result send error: {str(e)}')

    def define_environment(self, env):
        try:
            data = {
                "env_label": self.env_label,
                "environment": env
            }
            response = put(
                headers=self.headers,
                json=data,
                url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    suite_id=self.suite_id,
                    job_id=self.job_id
                )
            )
            print(f"Environment defined with code {response.status_code}")
            return response

        except Exception as e:
            print("Environment definition error: {}".format(str(e)))
