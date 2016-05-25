# coding: latin1
__author__ = 'bplesa'
import unittest
import os
from ConfigParser import SafeConfigParser
from test_utils import NobelRestClient
from itertools import product
from string import ascii_lowercase

STRINGS = {'u_nf': 'User not found!',
           'u_na': 'User not available!',
           'empty': 'Empty login not allowed!'}


class TestsCommon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg_file = 'nobel.cfg'
        assert os.path.isfile(cfg_file), \
                    'Config file ({cfg}) not found. Take a look at the nobel.cfg.example file.'.format(cfg=cfg_file)
        cfg = SafeConfigParser()
        cfg.read(cfg_file)
        cls.user = cfg.get('api', 'username')
        cls.password = cfg.get('api', 'password')
        cls.api_url = cfg.get('api', 'api_url')
        cls.n_client = NobelRestClient(api_url=cls.api_url)


class NobelRestTest(TestsCommon):

    def check_success_json(self, json_resp):
        return json_resp['success']

    def gen_users(self):
        # Quick'n dirty gen 5 all characters long strings
        return [''.join(i) for i in product(ascii_lowercase, repeat=5)]

    def test_login_with_provided(self):
        login = {'username': self.user,
                 'password': self.password}
        # setting the check flag to True verifies the Respose Code is 200
        r = self.n_client.login(login, check=True)
        self.assertTrue(self.check_success_json(r.json()), 'Did not get expected status message for correct user')
        # If we successfully login we should get a dict containing token and refreshToken
        self.assertTrue(r.json()['token'], 'Token field empty')
        self.assertTrue(r.json()['refreshToken'], 'refreshToken empty')
        # The two should not be the same
        self.assertTrue(r.json()['token'] != r.json()['refreshToken'], 'Token and refreshToken are the same')

    def test_login_with_bad_username(self):
        login = {'username': 'bad_username', 'password': self.password}
        r = self.n_client.login(login)
        # Assuming bad login attempt for mismatching credentials status code is 403
        self.assertEqual(r.status_code, 403, 'Got unexpected RC for bad username')
        # We should also check the response body for bad values in keys
        self.assertFalse(self.check_success_json(r.json()))
        self.assertTrue(r.json()['token'] == STRINGS['u_nf'])
        self.assertTrue(r.json()['refreshToken'] == STRINGS['u_nf'])

    def test_login_bad_pw(self):
        login = {'username': self.user,   'password': 'bad_password'}
        r = self.n_client.login(login)
        self.assertEqual(r.status_code, 403, 'Got unexpected RC for bad password')
        self.assertFalse(self.check_success_json(r.json()), 'Did not get expected success message for bad password')
        self.assertTrue(r.json()['token'] == STRINGS['u_na'], 'Did not get expected token message for bad password')
        self.assertTrue(r.json()['refreshToken'] == STRINGS['u_na'], 'Did not get expected refreshToken message')

    @unittest.skip('Dont wannt to bruteforce this run')
    def test_bruteforce_users(self):
        for user in self.gen_users():
            login = {'username': user, 'password': 'random_junk'}
            r = self.n_client.login(login)
            if r.json()['token'] != STRINGS['u_nf']:
                print 'Found a valid user: %s' %user

    def test_empty_login(self):
        r = self.n_client.login({})
        self.assertNotEqual(r.status_code, 200, 'Should not get 200 RC for empty client login')
        self.assertEquals(self.check_success_json(r.json()), False, 'Did not get expected success message for empty login')
        self.assertEquals(r.json()['token'], STRINGS['empty'], 'Did not get expected token message for empty login')
        self.assertEquals(r.json()['refreshToken'], STRINGS['empty'])

    def test_empty_user(self):
        login = {'username': '', 'password': 'test'}
        r = self.n_client.login(login)
        # Assuming the Response Code actually differes for a bad call, which it doesnt
        self.assertNotEqual(r.status_code, 200, 'Should not get 200 RC for empty client username')
        self.assertEqual(self.check_success_json(r.json()), False)
        # There should be an error message warning the user to not send an empty string as username

    def test_extended_latin_username(self):
        login = {'username': u'???', 'password': 'test'}
        r = self.n_client.login(login)
        self.assertNotEqual(r.status_code, 200, 'Should not get 200 RC for empty client username')
        self.assertEqual(self.check_success_json(r.json()), False)

    def test_not_json(self):
        login = True
        r = self.n_client.login(login)
        print r.json()
        print r.status_code
        self.assertEqual(r.status_code, 500)
        #TODO: No JSON in body generate exceptions
        #TODO: those exceptions are too verbose. Change the below asserts after the code is fixed
        assert False

if __name__ == '__main__':
    unittest.main(verbosity=2)