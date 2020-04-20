import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put


class Client:
    def __init__(
        self,
        build_id,
        suite_id,
        job_id,
        url,
        env_label,
    ):
        # TODO: in thread loading schema from api
        self.job_id = job_id
        self.url = url
        self.build_id = build_id
        self.env_label = env_label
        self.suite_id = suite_id

        # auth
        self.get_token()

    def get_token(self):
        request = post(
            url="{url}/user/login".format(url=self.url),
            auth=HTTPBasicAuth('dm1tryG', 'root'),
        )

        token = json.loads(request.content)["token"]
        self.token = token
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }

    def send_test_suite(self, res, env):
        data = {
            "test_cases_results": res,
            "environment": env,
            "env_label": self.env_label
        }
        request = post(
            headers=self.headers,
            data=json.dumps(data),
            url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                url=self.url,
                build_id=self.build_id,
                suite_id=self.suite_id,
                job_id=self.job_id
            )
        )
        print(request.content)

        return request

    def define_environment(self, env):
        data = {
            "env_label": self.env_label,
            "environment": env
        }
        request = put(
            headers=self.headers,
            data=json.dumps(data),
            url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                url=self.url,
                build_id=self.build_id,
                suite_id=self.suite_id,
                job_id=self.job_id
            )
        )
        return request
