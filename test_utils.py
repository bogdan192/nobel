__author__ = 'bplesa'
import requests

class NobelRestClient(object):
    def __init__(self, api_url):
        self.url = api_url
        # self.user = user
        # self.password = password

    def check_status(self, response, status=200, error=''):
        assert response.status_code == status, \
            'Expected status code %s but received %s:\n%s' % (status, response.status_code, response.text)
        if error:
            assert error in response.json['response']['error'], \
                'Expected error message %s but received:\n%s' % (error, response.text)
        return response

    def _get(self, endpoint, check=False, expected_status=200):
        r = requests.get(self.url + endpoint)
        if check:
            self.check_status(r, expected_status)
        return r

    def _post(self, endpoint, payload, check=False, expected_status=200):
        r = requests.post(self.url + endpoint, json=payload)
        if check:
            self.check_status(r, expected_status)
        return r

    def _put(self, endpoint, payload, check=False, expected_status=200):
        r = requests.put(self.url + endpoint, json=payload)
        if check:
            self.check_status(r, expected_status)
        return r

    def _delete(self, endpoint, check=False, expected_status=200):
        r = requests.delete(self.url + endpoint)
        if check:
            self.check_status(r, expected_status)
        return r

    def login(self, payload, check=False, expected_status=200):
        r = requests.post(self.url + '/login', json=payload)
        if check:
            self.check_status(r, expected_status)
        return r