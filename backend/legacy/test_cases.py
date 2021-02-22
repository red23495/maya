import json
import os
import requests
from requests.exceptions import RequestException
try:
    from .services.raw_request import RawRequestService
except:
    from services.raw_request import RawRequestService

__INDENT__ = 4

class AuthException(Exception):
    pass


def get_auth_session(options):
    host = options.get('host', 'http://127.0.0.1:8000').strip('/')
    token_url = "{host}/auth/accesstoken/".format(host=host)
    app_data = {
        "appname": options.get('appname', 'testing_tool'),
        "client_id": options.get('client_id', ''),
        "client_secret": options.get('client_secret', ''),
    }
    login_data = {
        "username": options.get('username', 'su'),
        "password": options.get('password', 'su')
    }
    session = requests.session()
    session.host = host

    try:
        response = session.post(token_url, app_data)
        token_resp = json.loads(response.content)
        session.access_token = token_resp['access_token']
        auth_dict = login_data.copy()
        auth_dict.update(app_data)
        auth_dict['access_token'] = session.access_token
        login_url = "{host}/auth/apilogin/".format(host=host)
        response = session.post(login_url, auth_dict)
        login_resp = json.loads(response.content)
        if login_resp['status'] != 'Success':
            raise AuthException('Authentication failed: {0}'.format(login_resp.get('msg')))
    except RequestException as e:
        raise AuthException('Could not connect to the server: {0}'.format(e))
    except ValueError as e:
        raise AuthException('Got unexpected response during api login: {0}'.format(e))
    return session


class TestCase(object):
    def __init__(self, test_file, session, db_mode=False):
        self.__db_mode = db_mode
        self.__session = session
        if db_mode:
            raw_request_id = int(test_file)
            self.__test_file = RawRequestService().get(raw_request_id).test_format
        else:
            with open(test_file) as test_file:
                self.__test_file = json.load(test_file)
        self.__output_response = {}

    def retrieve_response(self):
        host = self.__session.host
        path = self.__test_file['request']['path']
        query_str = self.__test_file['request']['META']['QUERY_STRING']
        headers = {  # for ajax request
            'X-Requested-With': self.__test_file['request']['META']['HTTP_X_REQUESTED_WITH']
        }
        url = '{}{}?{}'.format(host, path, query_str)
        if self.__test_file['request']['method'] == 'GET':
            response = self.__session.get(url, headers=headers, allow_redirects=False)
        else:
            response = self.__session.post(url, self.__test_file['request']['REQUEST'], headers=headers, allow_redirects=False)
        content_type = response.headers['Content-Type']
        output_response = {
            'content_type': content_type,
            'status_code': response.status_code,
        }
        if content_type == 'application/json':
            output_response['content'] = json.loads(response.content)
        elif content_type == 'application/xml':
            output_response['content'] = response.content
        else:
            output_response['content'] = ''
        self.__output_response = output_response
        return output_response

    # TODO: XML match actually compares expected and actual content as raw string
    def run(self):
        response = self.retrieve_response()
        result = {
            'name': self.__test_file['name'],
            'expected': self.__test_file['expected_response'],
            'actual': response,
            'index': self.__test_file['index'],
        }
        result['success'] = result['expected'] == result['actual']
        return result


def run_tests(test_case_file_names_list, db_mode=False):
    options_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'options.json')
    with open(options_file_path) as options_file:
        options = json.load(options_file)
        print(options)
    session = get_auth_session(options)
    test_results = []
    for file_name in test_case_file_names_list:
        if file_name:
            test_case = TestCase(file_name, session, db_mode=db_mode)
            test_results.append(test_case.run())
        else:
            test_results.append(None)
    return test_results

