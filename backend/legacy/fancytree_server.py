try:
    from SocketServer import ThreadingMixIn
except:
    from socketserver import ThreadingMixIn
import os
import sys
import time
from urllib import parse as urlparse
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from shutil import rmtree
import json
from datetime import datetime
from collections import deque
import re
try:
    from .services.filesystem import FilesystemService
except:
    from services.filesystem import FilesystemService
try:
    from .services.filesystem_requests import FilesystemRequestService
except:
    from services.filesystem_requests import FilesystemRequestService
try:
    from divineba.plugins.testing_tool.test_cases import run_tests
except:
    try:
        from test_cases import run_tests
    except:
        from .test_cases import run_tests
try:
    from .services.package import PackageService
except:
    from services.package import PackageService
try:
    from .services.test_cases import TestCaseService
except:
    from services.test_cases import TestCaseService
try:
    from .services.request import RequestService
except:
    from services.request import RequestService
try:
    from .services.play_record import PlayRecordService
except:
    from services.play_record import PlayRecordService
try:
    from . import env
except:
    import env
try:
    from . import config
except:
    import config

# ===============================================================================
# FancyTreeWsgiApp
# ===============================================================================

DB_MODE = env.DB_MODE
FILE_MODE = env.FILE_MODE

__OPERATION_MODE__ = config.OPERATION_MODE

class Exception404(Exception):
    pass


class Exception400(Exception):
    pass

__VERSION__ = 2

# version log
# 1 - initial version
# 2 - added database support


class FancyTreeWsgiApp(object):
    """This WSGI application serves a file system hierarchy for fancytree."""
    def __init__(self, option_dict):
        self.option_dict = option_dict
        self.root_dir = option_dict["root_path"]

    def __call__(self, environ, start_response):
        """Handle one HTTP request."""
        arg_list = urlparse.parse_qsl(environ.get("QUERY_STRING", ""))
        arg_dict = dict(arg_list)
        full_arg_dict = urlparse.parse_qs(environ.get("QUERY_STRING", ""))
        if arg_dict.get("sleep"):
            print("Sleeping %s seconds..." % arg_dict.get("sleep"))
            time.sleep(int(arg_dict.get("sleep")))
        try:
            response_list = self.serve_url(environ["PATH_INFO"], arg_dict, start_response, full_arg_dict)
            response_list = [res.encode('utf-8') for res in response_list]
            return response_list
        except Exception as e:
            start_response("200 ok", [("Content-Type", "application/json")])
            return [json.dumps({"error":str(e)})]

    def serve_url(self, url, query_dict, start_response, full_dict):
        if url == '/directory/' or url == '/directory':
            return self.serve_directory_listing(start_response)
        if url == '/play':
            return self.serve_play_request(query_dict, start_response)
        if url == '/package/new':
            return self.serve_package_create_request(query_dict, start_response)
        if url == '/package/rename':
            return self.serve_package_rename_request(query_dict, start_response)
        if url == '/test/rename':
            return self.serve_test_case_rename_request(query_dict, start_response)
        if url == '/test/select':
            return self.serve_test_case_select_request(query_dict, start_response)
        if url == '/test/move_up':
            return self.serve_test_case_move_up_request(query_dict, start_response)
        if url == '/test/move_down':
            return self.serve_test_case_move_down_request(query_dict, start_response)
        if url == '/package/move_up':
            return self.serve_package_move_up_request(query_dict, start_response)
        if url == '/package/move_down':
            return self.serve_package_move_down_request(query_dict, start_response)
        if url == '/test/move':
            return self.serve_test_case_move_to_package_request(query_dict, start_response)
        if url == '/package/move':
            return self.serve_package_move_to_package_request(query_dict, start_response)
        if url == '/test/delete':
            return self.serve_test_case_delete_request(query_dict, start_response)
        if url == '/package/delete':
            return self.serve_package_delete_request(query_dict, start_response)
        if url == '/request/select':
            return self.serve_request_select_request(query_dict, start_response)
        if url == '/request/status':
            return self.serve_request_set_status_request(query_dict, start_response)
        if url == '/request/move':
            return self.serve_request_move_to_test_case_request(query_dict, start_response)
        if url == '/request/delete':
            return self.serve_request_delete_request(query_dict, start_response)
        if url == '/request/move_up':
            return self.serve_request_move_up_request(query_dict, start_response)
        if url == '/request/move_down':
            return self.serve_request_move_down_request(query_dict, start_response)
        if url == '/request/rename':
            return self.serve_request_rename_request(query_dict, start_response)
        if url == '/test/new':
            return self.serve_test_case_create_request(query_dict, start_response)
        if url == '/package/select':
            return self.serve_package_select_request(query_dict, start_response)
        if url == '/filesystem/delete':
            return self.serve_filesystem_delete_request(query_dict, start_response)
        if url == '/request/delete/batch':
            return self.serve_requests_batch_delete(full_dict, start_response)
        if url == '/test/delete/batch':
            return self.serve_tests_batch_delete(full_dict, start_response)
        if url == '/package/delete/batch':
            return self.serve_packages_batch_delete(full_dict, start_response)
        if url == '/filesystem/delete/batch':
            return self.serve_filesystems_batch_delete(full_dict, start_response)
        if url == '/request/move/batch':
            return self.serve_batch_requests_move_to_test_case(full_dict, start_response)
        if url == '/test/move/batch':
            return self.serve_batch_tests_move_to_package(full_dict, start_response)
        if url == '/package/move/batch':
            return self.serve_batch_packages_move_to_package(full_dict, start_response)
        if url == '/cred':
            return self.serve_save_credential(query_dict, start_response)
        if url == '/cred/get':
            return self.serve_get_credential(query_dict, start_response)
        if url == '/version':
            return self.server_version_request(start_response)
        if url == '' or url == '/':
            start_response("302 REDIRECT", [("location", "index.html")])
            return []
        return self.serve_static_file(url, start_response)

    def serve_save_credential(self, query_dict, start_response):
        app_name = query_dict.get('app_name')
        client_id = query_dict.get('client_id')
        client_secret = query_dict.get('client_secret')
        start_response("200 OK", [("Content-Type", "plain/text")])
        return [self.save_credential(app_name, client_id, client_secret)]

    def serve_get_credential(self, query_dict, start_response):
        start_response("200 OK", [("Content-Type", "plain/text")])
        return [self.get_credential()]

    def serve_directory_listing(self, start_response):
        if __OPERATION_MODE__ == DB_MODE:
            return self.serve_directory_listing_from_db(start_response)
        test_dir_list = self.get_test_directory_list()
        test_file_dicts = []
        for directory in test_dir_list:
            directory_file_path = os.path.join(directory, 'filesystem.json')
            try:
                with open(directory_file_path, "r") as directory_file:
                    test_file_dicts.append({
                        "name": directory[len(self.root_dir):].strip('/'),
                        "test_file": json.load(directory_file)
                    })
            except Exception as e:
                start_response("500 ERROR", [("Content-Type", "application/json")])
                return [json.dumps({"error": 500, "msg": "error with directory listing occurred. {}".format(str(e))})]
        test_filesystems = []
        for test_file in test_file_dicts:
            test_filesystems.append(self.prepare_test_filesystem(test_file))
            directory_file_path = os.path.join(self.root_dir, test_file['name'], 'filesystem.json')
            with open(directory_file_path, 'w') as directory_file:
                directory_file.seek(0)
                json.dump(test_file['test_file'], directory_file, indent=4)
                directory_file.truncate()
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(test_filesystems)]

    # from db
    def serve_directory_listing_from_db(self, start_response):
        filesystems = self.get_all_filesystem_from_db()
        test_file_dicts = [{'name':data.name,'test_file': data} for data in filesystems]
        test_filesystems = []
        for test_file in test_file_dicts:
            test_filesystems.append(self.prepare_test_filesystem_from_db(test_file))
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(test_filesystems)]

    # from db
    def get_all_filesystem_from_db(self):
        return FilesystemService().all()

    # from db
    def prepare_test_filesystem_from_db(self, filesystem_dict):
        filesystem_model = filesystem_dict['test_file']
        ret_dict = {
            'name': filesystem_dict['name'],
            'test_file': filesystem_model.legacy_format
        }
        unorganized_requests = filesystem_model.unorganized_requests
        if not unorganized_requests:
            return ret_dict
        root_package = filesystem_model.package
        new_package_id = PackageService().create_package_with_timestamp(root_package.id).id
        requests = self.organize_requests_from_db(unorganized_requests)
        service = FilesystemRequestService()
        service.set_all_requests_as_processed(unorganized_requests)
        test_cases = self.organize_test_cases(requests)
        for tc in test_cases:
            tc_model = TestCaseService().import_from_legacy_dict(tc, package_id=new_package_id)
            tc['index'] = tc_model.id
            requets_list = tc['requests']
            for rq in requets_list:
                RequestService().import_from_legacy_dict(rq, test_case_id=tc_model.id)
        updated_fs = FilesystemService().get(filesystem_model.id)
        ret_dict['test_file'] = updated_fs.legacy_format
        return ret_dict

    # from db
    def organize_requests_from_db(self, request_models):
        requests = [request.raw_request.legacy_format for request in request_models]
        return requests

    def serve_play_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package', 'root')
        try:
            result = self.run_test(filesystem, package_path)
        except Exception as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status': 404, 'msg': str(e)})]
        if __OPERATION_MODE__ == DB_MODE:
            pr_service = PlayRecordService()
            pr_service.save_record(result, filesystem, package_path)
        else:
            store_file_name = str(datetime.now()).replace(' ', '_') + '.json'
            store_file_dir = os.path.join(self.root_dir, filesystem, 'played')
            if not os.path.exists(store_file_dir):
                os.makedirs(store_file_dir)
            store_file_path = os.path.join(store_file_dir, store_file_name)
            with open(store_file_path, 'w+') as play_file:
                json.dump(result, play_file, indent=4)
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_create_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        package_name = query_dict.get('package_name', 'new package')
        try:
            result = self.create_package(filesystem, package_path, package_name)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_rename_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        if package_path == 'root':
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, 'msg': "can't rename root package"})]
        package_name = query_dict.get('package_name', 'new package').strip()
        if package_name == 'root':
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, 'msg': "can't rename as root"})]
        try:
            result = self.rename_package(filesystem, package_path, package_name)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_rename_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        test_name = query_dict.get('test_name', 'default name')
        try:
            result = self.rename_test_case(filesystem, package_path, test_no, test_name)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_select_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        test_select = query_dict.get('selected')
        try:
            result = self.select_test_case(filesystem, package_path, test_no, test_select)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_move_up_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        try:
            result = self.move_test_case_up(filesystem, package_path, test_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_move_down_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        try:
            result = self.move_test_case_down(filesystem, package_path, test_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_move_down_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        package_no = query_dict.get('package_no')
        try:
            result = self.move_package_down(filesystem, package_path, package_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_move_up_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        package_no = query_dict.get('package_no')
        try:
            result = self.move_package_up(filesystem, package_path, package_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_move_to_package_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        from_package_path = query_dict.get('from_package', 'root')
        to_package_path = query_dict.get('to_package', 'root')
        test_no = query_dict.get('test_no')
        try:
            result = self.move_test_case_to_package(filesystem, from_package_path, test_no, to_package_path)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_move_to_package_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        from_package_path = query_dict.get('from_package', 'root')
        to_package_path = query_dict.get('to_package', 'root')
        package_no = query_dict.get('package_no')
        try:
            result = self.move_package_to_package(filesystem, from_package_path, package_no, to_package_path)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_delete_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no', '-1')
        try:
            result = self.delete_test_case(filesystem, package_path, test_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_delete_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        parent_package_path = query_dict.get('package_path', 'root')
        package_no = query_dict.get('package_no', '-1')
        try:
            result = self.delete_package(filesystem, parent_package_path, package_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_select_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        request_no = query_dict.get('request_no')
        request_select = query_dict.get('selected', None)
        try:
            result = self.select_request(filesystem, package_path, test_no, request_no, request_select)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_set_status_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        request_no = query_dict.get('request_no')
        status = query_dict.get('status')
        if status.upper() not in ['SUCCESS', 'ERROR', 'OK']:
            status = 'OK'
        try:
            result = self.set_request_status(filesystem, package_path, test_no, request_no, status)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_move_to_test_case_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        from_package_path = query_dict.get('from_package', 'root')
        to_package_path = query_dict.get('to_package', 'root')
        from_test_no = query_dict.get('from_test', None)
        to_test_no = query_dict.get('to_test', None)
        request_no = query_dict.get('request', None)
        try:
            result = self.move_request_to_test_case(
                filesystem, from_package_path, from_test_no, request_no, to_package_path, to_test_no
            )
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_delete_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no')
        request_no = query_dict.get('request_no')
        try:
            result = self.delete_request(filesystem, package_path, test_no, request_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_move_up_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no', None)
        request_no = query_dict.get('request_no')
        try:
            result = self.move_request_up(filesystem, package_path, test_no, request_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_move_down_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no', None)
        request_no = query_dict.get('request_no')
        try:
            result = self.move_request_down(filesystem, package_path, test_no, request_no)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception400 as e:
            start_response("400 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 400, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_request_rename_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_no = query_dict.get('test_no', None)
        request_no = query_dict.get('request_no')
        request_name = query_dict.get('request_name', 'request')
        try:
            result = self.rename_request(filesystem, package_path, test_no, request_no, request_name)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_test_case_create_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        test_name = query_dict.get('test_name', 'new package')
        try:
            result = self.create_test_case(filesystem, package_path, test_name)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_package_select_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        package_path = query_dict.get('package_path', 'root')
        package_selected = query_dict.get('selected')
        try:
            result = self.select_package(filesystem, package_path, package_selected)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_filesystem_delete_request(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', '')
        try:
            result = self.delete_filesystem(filesystem)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_requests_batch_delete(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        requests = query_dict.get('requests', query_dict.get('requests[]', []))
        try:
            result = self.batch_delete_requests(filesystem, requests)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_tests_batch_delete(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        tests = query_dict.get('tests', query_dict.get('tests[]', []))
        try:
            result = self.batch_delete_tests(filesystem, tests)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_packages_batch_delete(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        packages = query_dict.get('packages', query_dict.get('packages[]', []))
        try:
            result = self.batch_delete_packages(filesystem, packages)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_filesystems_batch_delete(self, query_dict, start_response):
        filesystems = query_dict.get('filesystems', query_dict.get('filesystems[]', []))
        try:
            result = self.batch_delete_filesystems(filesystems)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_batch_requests_move_to_test_case(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        requests = query_dict.get('requests', query_dict.get('requests[]', []))
        to_test = query_dict.get('to_test', [None])[0]
        try:
            result = self.batch_move_requests_to_test_case(filesystem, requests, to_test)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_batch_tests_move_to_package(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        tests = query_dict.get('tests', query_dict.get('tests[]', []))
        to_package = query_dict.get('to_package', [None])[0]
        try:
            result = self.batch_move_test_cases_to_package(filesystem, tests, to_package)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_batch_packages_move_to_package(self, query_dict, start_response):
        filesystem = query_dict.get('filesystem', [''])[0]
        packages = query_dict.get('packages', query_dict.get('packages[]', []))
        to_package = query_dict.get('to_package', [None])[0]
        try:
            result = self.batch_move_packages_to_package(filesystem, packages, to_package)
        except Exception404 as e:
            start_response("404 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({'status_code': 404, "msg": str(e)})]
        except Exception as e:
            start_response("500 ERROR", [("Content-Type", "application/json")])
            return [json.dumps({"status_code": 500, "msg": str(e)})]
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(result)]

    def serve_static_file(self, file_name, start_response):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', file_name.strip('/'))
        try:
            with open(file_path) as static_file:
                file_content = static_file.read()
                extension = file_name.strip('/').split('.')[-1]
                if extension == 'htm' or extension == 'html':
                    start_response("200 OK", [("Content-Type", "text/html")])
                elif extension == 'js':
                    start_response("200 OK", [("Content-Type", "text/javascript")])
                elif extension == 'css':
                    start_response("200 OK", [("Content-Type", "text/css")])
                else:
                    start_response("200 OK", [("Content-Type", "text/plain")])
                return [file_content]
        except:
            start_response("404 ERROR", [("Content-Type", "text/plain")])
            return ["Page Not Found!"]

    def server_version_request(self, start_response):
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps({'version': __VERSION__})]

    def get_test_directory_list(self):
        directories = os.walk(self.root_dir)
        test_directories = []
        for (root, directory_list, file_list) in directories:
            if "filesystem.json" in file_list:
                test_directories.append(root)
        return test_directories

    def get_directory_list_from_db(self):
        service = FilesystemService()
        return service.get_all_filesystem_name()

    def prepare_test_filesystem(self, filesystem_dict):
        unorganized_requests = filesystem_dict['test_file'].get('unorganized_requests', [])
        if not unorganized_requests:
            return filesystem_dict
        directory_name = filesystem_dict['name']
        requests = self.organize_requests(directory_name, unorganized_requests)
        filesystem_dict['test_file']['unorganized_requests'] = []
        # the sort is not required, as the steps are recorded in order any way
        # it is still added so that no future change can change the expected behaviour of this function
        requests.sort(key=lambda request: request["index"])
        test_cases = self.organize_test_cases(requests)
        test_index = filesystem_dict['test_file'].get('test_index', 0)
        test_index = self.assign_index_to_test_cases(test_cases, test_index)
        filesystem_dict['test_file']['test_index'] = test_index
        if 'packages' not in filesystem_dict['test_file']:
            filesystem_dict['test_file']['packages'] = [{
                "dir": "root",
                "test_cases": [],
                "packages": [],
                "selected": True,
            }]
        package = self.get_package(filesystem_dict['test_file'], 'root')
        new_package = {
            "dir": str(datetime.now()).replace(' ', '_').replace(':', '_').replace('.', '_'),
            "test_cases": test_cases,
            "packages": [],
            "selected": True,
        }
        package['packages'].append(new_package)
        return filesystem_dict

    def assign_index_to_test_cases(self, test_cases, start_index):
        for test in test_cases:
            test['index'] = start_index
            start_index = start_index + 1
        return start_index

    def organize_requests(self, directory_name, request_file_names):
        requests = []
        for file_name in request_file_names:
            request_file_path = os.path.join(self.root_dir, directory_name, 'steps', file_name)
            with open(request_file_path) as request_file:
                request_data = json.load(request_file)
                request_object = {
                    'file': request_file_path,
                    'index': request_data['index'],
                    'content_type': request_data['expected_response']['content_type'],
                    'method': request_data['request']['method'],
                    'status_code': request_data['expected_response']['status_code'],
                    'name': request_data['name'],
                    'path': request_data['request']['path'],
                    'selected': request_data['request']['method'].lower() == 'post' or
                                'application/json' in request_data['expected_response']['content_type'],
                    'status': self.get_request_status(
                        request_data['request']['method'],
                        request_data['expected_response']['status_code']),
                    'data': request_data['request']['REQUEST'],
                }
                requests.append(request_object)
        return requests

    def get_request_status(self, method, status_code):
        if method.lower() == 'get':
            return 'OK'
        if method.lower() == 'post':
            return 'SUCCESS' if status_code//100 == 3 else 'ERROR'

    def organize_test_cases(self, request_list):
        test_cases = []
        request_holder = []
        for request in request_list:
            if 'text/html' in request['content_type']:
                if request_holder:
                    test_cases.append(request_holder)
                request_holder = [request]
            else:
                request_holder.append(request)
        if request_holder:
            test_cases.append(request_holder)
        test_cases = self.join_redirects_in_test_cases(test_cases)
        test_cases = list(map(lambda case: {'name': '', 'selected': True, 'requests': case}, test_cases))
        test_cases = self.set_default_selected_for_test_cases(test_cases)
        test_cases = self.set_default_title_for_test_cases(test_cases)
        return test_cases

    def set_default_selected_for_test_cases(self, test_case_list):
        for test_case in test_case_list:
            # hotfix for default value error
            # if already not wrapped inside a list, wrap it
            # try:
            #     if len(test_case.get('requests', [])) > 0:
            #         test_case['selected'] = test_case['requests'][0]['method'].lower() == 'post'
            # except:
            #     pass
            test_case['selected'] = True
        return test_case_list

    def set_default_title_for_test_cases(self, test_case_list):
        for test_case in test_case_list:
            title = ''
            main_request = test_case['requests'][0]
            if main_request['method'].lower() == 'get':
                if main_request['status_code'] // 100 == 2:
                    title = 'Fetched {} page'.format(main_request['name'])
            elif main_request['method'].lower() == 'post':
                if main_request['status_code'] // 100 == 2:
                    title = 'Error submitting data in {}'.format(main_request['name'])
                elif main_request['status_code'] // 100 == 3:
                    title = 'Successfully submitted data in {}'.format(main_request['name'])
            test_case['name'] = title
        return test_case_list

    def join_redirects_in_test_cases(self, test_cases):
        return_list = []
        chained_list = []
        chain = False
        for case in test_cases:
            if chain:
                if case[0]['status_code'] // 100 == 3:
                    chained_list += case
                else:
                    chained_list += case
                    return_list.append(chained_list)
                    chained_list = []
                    chain = False
            else:
                if case[0]['status_code'] // 100 == 3:
                    chain = True
                    chained_list += case
                else:
                    return_list.append(case)
        if chained_list:
            return_list += chained_list
        return return_list

    def get_package(self, filesystem, package_path):
        package_path_list = package_path.strip('/').split('/')
        if 'packages' not in filesystem:
            return None
        packages = filesystem['packages']
        return self.__get_package(packages, package_path_list)

    def __get_package(self, package_list, path_as_list):
        target_package = None
        for package in package_list:
            if 'dir' in package and package['dir'] == path_as_list[0]:
                target_package = package
                break
        if not target_package:
            return None
        if len(path_as_list) == 1:
            return target_package
        return self.__get_package(target_package.get('packages', []), path_as_list[1:])

    def run_test(self, filesystem_name, package_path):
        if __OPERATION_MODE__ == DB_MODE:
            filesystem = FilesystemService().get_filesystem_by_name(filesystem_name).legacy_format
        else:
            filesystem_path = os.path.join(self.root_dir, filesystem_name, 'filesystem.json')
            with open(filesystem_path) as filesystem_file:
                filesystem = json.load(filesystem_file)
        package = self.get_package(filesystem, package_path)
        if not package:
            raise LookupError
        packages = self.run_child_packages([package])
        success = True
        for package in packages:
            if package is not None:
                success = success and package['success']
        response = {
            'filesystem': filesystem_name,
            'packages': packages,
            'success': success,
        }
        return response

    def run_child_packages(self, package_list):
        result_packages = []
        for package in package_list:
            if not package['selected']:
                result_packages.append(None)
                continue
            success = True
            test_cases = self.run_package(package)
            for test in test_cases:
                if test is not None:
                    success = success and test['success']
            child_packages = self.run_child_packages(package.get('packages', []))
            for child_package in child_packages:
                if child_package is not None:
                    success = success and child_package['success']
            result_packages.append({
                'dir': package['dir'],
                'test_cases': test_cases,
                'packages': child_packages,
                'success': success,
            })
        return result_packages

    def run_package(self, package):
        test_case_results = []
        test_cases = package.get('test_cases', [])
        for test_case in test_cases:
            if test_case['selected']:
                ret = self.run_test_case(test_case)
                success = True
                for request in ret['requests']:
                    if request is not None:
                        success = success and request['success']
                ret["name"] = test_case["name"]
                ret["success"] = success
                test_case_results.append(ret)
            else:
                test_case_results.append(None)
        return test_case_results

    def run_test_case(self, test_case):
        requests = test_case.get('requests', [])
        request_file_names = []
        for request in requests:
            if request['selected']:
                request_file_names.append(request["file"])
            else:
                request_file_names.append(None)
        db_mode = False
        if __OPERATION_MODE__ == DB_MODE:
            db_mode = True
        request_results = run_tests(request_file_names, db_mode=db_mode)
        return {"requests": request_results, "index": test_case.get('index')}

    def create_package(self, filesystem, package_path, package_name):
        if __OPERATION_MODE__ == DB_MODE:
            return self.create_package_from_db(filesystem, package_path, package_name)
        package_name = package_name.replace('/', '_')
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            parent_package = self.get_package(filesystem_dict, package_path)
            if not parent_package:
                raise Exception404('Parent package not found')
            package_children = parent_package.get('packages', [])
            is_unique_name = True
            for child in package_children:
                if child['dir'] == package_name:
                    is_unique_name = False
                    break
            if not is_unique_name:
                raise Exception400('A package with the name {} already exists'.format(package_name))
            package_children.append({
                'dir': package_name,
                'test_cases': [],
                'packages': [],
                'selected': False,
            })
            parent_package['packages'] = package_children
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
        return {'status_code': 200, 'msg': 'Successfully created package {}'.format(package_name)}

    # from db
    def create_package_from_db(self, filesystem_name, package_path, package_name):
        package_name = package_name.replace('/', '_')
        service = FilesystemService()
        filesystem = service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if not parent_package:
            raise Exception404('Parent package not found')
        is_unique_name = True
        for child in parent_package.children:
            if child.dir == package_name:
                is_unique_name = False
                break
        if not is_unique_name:
            raise Exception400('A package with the name {} already exists'.format(package_name))
        package_service = PackageService()
        package_service.create_package(package_name, parent_package.id)
        return {'status_code': 200, 'msg': 'Successfully created package {}'.format(package_name)}

    def rename_package(self, filesystem, package_path, package_name):
        if __OPERATION_MODE__ == DB_MODE:
            return self.rename_package_from_db(filesystem, package_path, package_name)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            parent_package = self.get_package(filesystem_dict, '/'.join(package_path.strip('/').split('/')[:-1]))
            package_children = parent_package['packages']
            is_unique_name = True
            for child in package_children:
                if child['dir'] == package_name:
                    is_unique_name = False
                    break
            if not is_unique_name:
                raise Exception400('A package with the name {} already exists'.format(package_name))
            package['dir'] = package_name
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
        return {'status_code': 200, 'msg': 'Successfully renamed package {}'.format(package_name)}

    # from db
    def rename_package_from_db(self, filesystem_name, package_path, package_name):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        package = filesystem.get_package_by_path(package_path)
        try:
            package.rename(package_name)
        except Exception as e:
            raise Exception400(str(e))
        fs_service.save(package)
        return {'status_code': 200, 'msg': 'Successfully renamed package {}'.format(package_name)}

    def rename_test_case(self, filesystem, package_path, test_no, test_name):
        if __OPERATION_MODE__ == DB_MODE:
            return self.rename_test_case_from_db(filesystem, package_path, test_no, test_name)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            target_test_case['name'] = test_name
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully renamed test case {}'.format(test_name)}

    # from db
    def rename_test_case_from_db(self, filesystem_name, package_path, test_no, test_name):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        try:
            target_test_case = filesystem.get_test_case_by_index(package_path, int(test_no))
        except Exception as e:
            raise Exception404(str(e))
        target_test_case.name = test_name
        fs_service.save(target_test_case)
        return {'status_code': 200, 'msg': 'Successfully renamed test case {}'.format(test_name)}

    def select_test_case(self, filesystem, package_path, test_no, test_selected):
        if __OPERATION_MODE__ == DB_MODE:
            return self.select_test_case_from_db(filesystem, package_path, test_no, test_selected)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            target_test_case['selected'] = bool(test_selected)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully set test case {}'.format(bool(test_selected))}

    # from db
    def select_test_case_from_db(self, filesystem_name, package_path, test_no, test_selected):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        tc = filesystem.get_test_case_by_index(package_path, int(test_no))
        tc.selected = bool(test_selected)
        fs_service.save(tc)
        return {'status_code': 200, 'msg': 'Successfully set test case {}'.format(bool(test_selected))}

    def move_test_case_up(self, filesystem, package_path, test_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_test_case_up_from_db(filesystem, package_path, test_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            test_no = int(test_no)
            if test_no == 0:
                raise Exception400("Can't move test case 0 any higher")
            if test_no < 0:
                raise Exception400('Test no can\'t be lower than 0')
            try:
                upper = test_cases[test_no - 1]
                lower = test_cases[test_no]
                test_cases[test_no], test_cases[test_no - 1] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved test case up.'}

    # from db
    def move_test_case_up_from_db(self, filesystem_name, package_path, test_no):
        test_no = int(test_no)
        if test_no == 0:
            raise Exception400("Can't move test case 0 any higher")
        if test_no < 0:
            raise Exception400('Test no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if test_no >= len(parent_package.test_cases):
            raise Exception400('Test index out of bound')
        upper_test_case = parent_package.test_cases[test_no - 1]
        lower_test_case = parent_package.test_cases[test_no]
        upper_test_case.execution_order, lower_test_case.execution_order = lower_test_case.execution_order, upper_test_case.execution_order
        fs_service.save(upper_test_case)
        fs_service.save(lower_test_case)
        return {'status_code': 200, 'msg': 'Successfully moved test case up.'}

    def move_test_case_down(self, filesystem, package_path, test_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_test_case_down_from_db(filesystem, package_path, test_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            test_no = int(test_no)
            if test_no == len(test_cases) - 1:
                raise Exception400("Can't move test case any lower")
            if test_no < 0:
                raise Exception400('Test no can\'t be lower than 0')
            try:
                upper = test_cases[test_no]
                lower = test_cases[test_no + 1]
                test_cases[test_no + 1], test_cases[test_no] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved test case down.'}

    # from db
    def move_test_case_down_from_db(self, filesystem_name, package_path, test_no):
        test_no = int(test_no)
        if test_no < 0:
            raise Exception400('Test no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if test_no >= len(parent_package.test_cases):
            raise Exception400('Test index out of bound')
        if test_no == len(parent_package.test_cases) - 1:
            raise Exception400("Can't move test case any lower")
        upper_test_case = parent_package.test_cases[test_no]
        lower_test_case = parent_package.test_cases[test_no + 1]
        upper_test_case.execution_order, lower_test_case.execution_order = lower_test_case.execution_order, upper_test_case.execution_order
        fs_service.save(upper_test_case)
        fs_service.save(lower_test_case)
        return {'status_code': 200, 'msg': 'Successfully moved test case up.'}

    def move_package_down(self, filesystem, parent_package_path, package_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_package_down_from_db(filesystem, parent_package_path, package_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, parent_package_path)
            if not package:
                raise Exception404('Parent package not found')
            packages = package['packages']
            package_no = int(package_no)
            if package_no == len(packages) - 1:
                raise Exception400("Can't move package any lower")
            if package_no < 0:
                raise Exception400('Package no can\'t be lower than 0')
            try:
                upper = packages[package_no]
                lower = packages[package_no + 1]
                packages[package_no + 1], packages[package_no] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved package down.'}

    # from db
    def move_package_down_from_db(self, filesystem_name, package_path, package_no):
        package_no = int(package_no)
        if package_no < 0:
            raise Exception400('Package no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if package_no >= len(parent_package.children):
            raise Exception400('Package index out of bound')
        if package_no == len(parent_package.children) - 1:
            raise Exception400("Can't move package any lower")
        upper_package = parent_package.children[package_no]
        lower_package = parent_package.children[package_no + 1]
        upper_package.execution_order, lower_package.execution_order = lower_package.execution_order, upper_package.execution_order
        fs_service.save(upper_package)
        fs_service.save(lower_package)
        return {'status_code': 200, 'msg': 'Successfully moved package up.'}

    def move_package_up(self, filesystem, parent_package_path, package_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_package_up_from_db(filesystem, parent_package_path, package_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, parent_package_path)
            if not package:
                raise Exception404('Parent package not found')
            packages = package['packages']
            package_no = int(package_no)
            if package_no == 0:
                raise Exception400("Can't move package any higher")
            if package_no < 0:
                raise Exception400('Package no can\'t be lower than 0')
            try:
                upper = packages[package_no - 1]
                lower = packages[package_no]
                packages[package_no], packages[package_no - 1] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved package up.'}

    # from db
    def move_package_up_from_db(self, filesystem_name, package_path, package_no):
        package_no = int(package_no)
        if package_no == 0:
            raise Exception400("Can't move package any higher")
        if package_no < 0:
            raise Exception400('Package no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if package_no >= len(parent_package.children):
            raise Exception400('Package index out of bound')
        upper_package = parent_package.children[package_no - 1]
        lower_package = parent_package.children[package_no]
        upper_package.execution_order, lower_package.execution_order = lower_package.execution_order, upper_package.execution_order
        fs_service.save(upper_package)
        fs_service.save(lower_package)
        return {'status_code': 200, 'msg': 'Successfully moved package up.'}

    def move_test_case_to_package(self, filesystem, from_package_path, test_no, to_package_path):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_test_case_to_package_from_db(filesystem, from_package_path, test_no, to_package_path)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            from_package = self.get_package(filesystem_dict, from_package_path)
            if not from_package:
                raise Exception404('From package not found')
            to_package = self.get_package(filesystem_dict, to_package_path)
            if not to_package:
                raise Exception404('To package not found')
            test_no = int(test_no)
            from_test_cases = from_package['test_cases']
            to_test_cases = to_package['test_cases']
            if test_no < 0:
                raise Exception400('Test no can\'t be negative')
            try:
                target_test_case = from_test_cases.pop(test_no)
                to_test_cases.append(target_test_case)
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {
                'status_code': 200,
                'msg': 'Successfully moved test case from {} to {}.'.format(from_package_path, to_package_path)
            }

    # from db
    def move_test_case_to_package_from_db(self, filesystem_name, from_package_path, test_no, to_package_path):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        try:
            test_case = filesystem.get_test_case_by_index(from_package_path, int(test_no))
        except Exception as e:
            return Exception404(str(e))
        to_package = filesystem.get_package_by_path(to_package_path)
        test_case.package_id = to_package.id
        tc_id = test_case.id
        fs_service.save(test_case)
        fs_service.refresh(to_package)
        to_package.move_test_case_to_bottom(tc_id)
        fs_service.save(to_package)
        return {
                'status_code': 200,
                'msg': 'Successfully moved test case from {} to {}.'.format(from_package_path, to_package_path)
            }

    def move_package_to_package(self, filesystem, current_parent_path, package_no, target_parent_path):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_package_to_package_from_db(filesystem, current_parent_path, package_no, target_parent_path)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package_no = int(package_no)
            current_parent = self.get_package(filesystem_dict, current_parent_path)
            if current_parent is None:
                raise Exception404('Package not found')
            target_parent = self.get_package(filesystem_dict, target_parent_path)
            if target_parent is None:
                raise Exception404('Destination package not found')
            if current_parent_path.strip('/') == target_parent_path.strip('/'):
                raise Exception400('Cannot move to it\'s present package')
            if package_no < 0:
                raise Exception400('Package no can\'t be negative')
            try:
                target_package = current_parent['packages'].pop(package_no)
                target_package_full_path = "/".join([current_parent_path, target_package['dir']])
                if target_parent_path.strip('/').startswith(target_package_full_path.strip('/')):
                    raise Exception400('Can not move to it\'s own child.')
                is_unique_name = True
                for child in target_parent['packages']:
                    if child['dir'] == target_package['dir']:
                        is_unique_name = False
                        break
                if not is_unique_name:
                    raise Exception400('A package with the name {} already exists'.format(target_package['dir']))
                target_parent['packages'].append(target_package)
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {
                'status_code': 200,
                'msg': 'Successfully moved package from {} to {}.'.format(current_parent_path, target_parent_path)
            }

    # from db
    def move_package_to_package_from_db(self, filesystem_name, current_parent_path, package_no, target_parent_path):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        try:
            package = filesystem.get_package_by_path(current_parent_path).children[int(package_no)]
        except Exception as e:
            return Exception404(str(e))
        to_package = filesystem.get_package_by_path(target_parent_path)
        if package.has_child(to_package):
            raise Exception400('Can\'t move inside it\'s own child.')
        if to_package.has_child_by_name(package.dir):
            raise Exception400('Already has a child by this name')
        package.parent_package_id = to_package.id
        pkg_id = package.id
        fs_service.save(package)
        fs_service.refresh(to_package)
        to_package.move_package_to_bottom(pkg_id)
        fs_service.save(to_package)
        return {
                'status_code': 200,
                'msg': 'Successfully moved package from {} to {}.'.format(current_parent_path, target_parent_path)
            }

    def delete_test_case(self, filesystem, package_path, test_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.delete_test_case_from_db(filesystem, package_path, test_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_no = int(test_no)
            if test_no < 0:
                raise Exception400('Test no can\'t be lower than 0')
            try:
                package['test_cases'].pop(test_no)
            except Exception as e:
                raise Exception404(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {
                'status_code': 200,
                'msg': 'Successfully deleted test case',
            }

    # from db
    def delete_test_case_from_db(self, filesystem_name, package_path, test_no):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        tc = filesystem.get_test_case_by_index(package_path, int(test_no))
        fs_service.delete(tc)
        return {
                'status_code': 200,
                'msg': 'Successfully deleted test case',
            }

    def delete_package(self, filesystem, parent_package_path, package_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.delete_package_from_db(filesystem,parent_package_path,package_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, parent_package_path)
            if not package:
                raise Exception404('Package not found')
            package_no = int(package_no)
            if package_no < 0:
                raise Exception400('Package no can\'t be lower than 0')
            try:
                package['packages'].pop(package_no)
            except Exception as e:
                raise Exception404(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {
                'status_code': 200,
                'msg': 'Successfully deleted package',
            }

    # from db
    def delete_package_from_db(self, filesystem_name, parent_package_path, package_no):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent = filesystem.get_package_by_path(parent_package_path)
        package = parent.children[int(package_no)]
        if package.is_root():
            raise Exception400('Can\'t delete root package.')
        fs_service.delete(package)
        return {
                'status_code': 200,
                'msg': 'Successfully package case',
            }


    def select_request(self, filesystem, package_path, test_no, request_no, request_selected):
        if __OPERATION_MODE__ == DB_MODE:
            return self.select_request_from_db(
                filesystem, package_path, int(test_no), int(request_no), bool(request_selected)
            )
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            requests = target_test_case['requests']
            target_request = requests[int(request_no)]
            target_request['selected'] = bool(request_selected)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully set request {}'.format(bool(request_selected))}

    # from db
    def select_request_from_db(self, filesystem_name, package_path, test_no, request_no, request_selected):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        rq = filesystem.get_request_by_index(package_path, test_no, request_no)
        rq.selected = bool(request_selected)
        fs_service.save(rq)
        return {'status_code': 200, 'msg': 'Successfully set request {}'.format(bool(request_selected))}

    def set_request_status(self, filesystem, package_path, test_no, request_no, status):
        if __OPERATION_MODE__ == DB_MODE:
            return self.set_request_status_from_db(filesystem, package_path, int(test_no), int(request_no), status)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            requests = target_test_case['requests']
            target_request = requests[int(request_no)]
            target_request['status'] = status
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully set request status as {}'.format(status)}

    # from db
    def set_request_status_from_db(self, filesystem_name, package_path, test_no, request_no, status):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        rq = filesystem.get_request_by_index(package_path, test_no, request_no)
        rq.status = status
        fs_service.save(rq)
        return {'status_code': 200, 'msg': 'Successfully set request status {}'.format(status)}

    def move_request_to_test_case(
            self, filesystem, from_package_path, from_test_no, request_no, to_package_path, to_test_no
    ):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_request_to_test_case_from_db(filesystem, from_package_path, from_test_no, request_no, to_package_path, to_test_no)
        request_no = int(request_no)
        if request_no < 0:
            raise Exception400('Request no can\'t be negative')
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            from_package = self.get_package(filesystem_dict, from_package_path)
            if not from_package:
                raise Exception404('From package not found')
            to_package = self.get_package(filesystem_dict, to_package_path)
            if not to_package:
                raise Exception404('To package not found')
            from_test_no = int(from_test_no)
            to_test_no = int(to_test_no)
            from_test_cases = from_package['test_cases']
            to_test_cases = to_package['test_cases']
            from_requests = from_test_cases[from_test_no]['requests']
            to_requests = to_test_cases[to_test_no]['requests']
            if from_test_no < 0 or to_test_no < 0:
                raise Exception400('Test no can\'t be negative')
            try:
                target_request = from_requests.pop(request_no)
                to_requests.append(target_request)
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {
                'status_code': 200,
                'msg': 'Successfully moved request'
            }

    # from db
    def move_request_to_test_case_from_db(self, filesystem_name, from_package_path, from_test_no, request_no, to_package_path, to_test_no):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        try:
            request = filesystem.get_request_by_index(from_package_path, int(from_test_no), int(request_no))
        except Exception as e:
            return Exception404(str(e))
        to_test = filesystem.get_test_case_by_index(to_package_path, int(to_test_no))
        request.test_case_id = to_test.id
        rq_id = request.id
        fs_service.save(request)
        fs_service.refresh(to_test)
        to_test.move_request_to_bottom(rq_id)
        fs_service.save(to_test)
        return {
                'status_code': 200,
                'msg': 'Successfully moved request'
            }


    def delete_request(self, filesystem, package_path, test_no, request_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.delete_request_from_db(filesystem, package_path, test_no, request_no)
        request_no = int(request_no)
        if request_no < 0:
            raise Exception400('Request no can\'t be negative')
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            requests = target_test_case['requests']
            requests.pop(request_no)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully deleted request'}

    # from db
    def delete_request_from_db(self, filesystem_name, package_path, test_no, request_no):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        request = filesystem.get_request_by_index(package_path, int(test_no), int(request_no))
        fs_service.delete(request)
        return {
            'status_code': 200,
            'msg': 'Successfully package case',
        }

    def batch_delete_requests(self, filesystem, requests):
        if __OPERATION_MODE__ == DB_MODE:
            requests = [int(req) for req in requests]
            return self.batch_delete_requests_from_db(filesystem, requests)
        requests = map(int, requests)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            PACKAGE_T = 'package'
            TEST_T = 'test'
            requests_queue = deque()
            requests_queue.append((filesystem_dict['packages'][0], PACKAGE_T))
            while len(requests_queue) > 0:
                node, nodetype = requests_queue.popleft()
                if nodetype == PACKAGE_T:
                    for test in node["test_cases"]:
                        requests_queue.append((test, TEST_T))
                    for package in node["packages"]:
                        requests_queue.append((package, PACKAGE_T))
                if nodetype == TEST_T:
                    filtered_requests = filter(lambda request: request["index"] not in requests, node["requests"])
                    node["requests"] = list(filtered_requests)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully deleted {} requests'.format(requests)}

    # from db
    def batch_delete_requests_from_db(self, filesystem_name, requests):
        service = RequestService()
        for _id in requests:
            service.delete(_id)
        return {'status_code': 200, 'msg': 'Successfully deleted {} requests'.format(requests)}

    def batch_delete_tests(self, filesystem, tests):
        tests = map(int, tests)
        if __OPERATION_MODE__ == DB_MODE:
          return self.batch_delete_tests_from_db(filesystem, tests)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            tests_queue = deque()
            tests_queue.append(filesystem_dict['packages'][0])
            while len(tests_queue) > 0:
                node = tests_queue.popleft()
                for package in node["packages"]:
                    tests_queue.append(package)
                filtered_tests = filter(lambda test: test["index"] not in tests, node["test_cases"])
                node["test_cases"] = list(filtered_tests)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully deleted {} test cases'.format(tests)}

    # from db
    def batch_delete_tests_from_db(self, filesystem_name, tests):
        service = TestCaseService()
        for _id in tests:
            service.delete(_id)
        return {'status_code': 200, 'msg': 'Successfully deleted {} test cases'.format(tests)}

    def batch_delete_packages(self, filesystem, packages):
        if __OPERATION_MODE__ == DB_MODE:
            return self.batch_delete_packages_from_db(filesystem, packages)
        TO_BE_DELETED_FLAG = '___TO_BE_DELETED___'
        packages = map(lambda pack: pack.strip('/'), packages)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            packages_queue = deque()
            packages_queue.append((filesystem_dict['packages'][0], ''))
            while len(packages_queue) > 0:
                node, parent_name = packages_queue.popleft()
                node_name = node["dir"]
                package_name = parent_name + node_name
                for package in node["packages"]:
                    child_package_name = package_name + '/' + package['dir']
                    print(child_package_name)
                    if child_package_name in packages:
                        package[TO_BE_DELETED_FLAG] = True
                    else:
                        packages_queue.append((package, package_name + '/'))
                node["packages"] = filter(lambda pack: not pack.get(TO_BE_DELETED_FLAG, False), node["packages"])

            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully deleted {} packages'.format(packages)}

    # from db
    def batch_delete_packages_from_db(self, filesystem_name, packages):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        for pkg_path in packages:
            pkg = filesystem.get_package_by_path(pkg_path)
            fs_service.delete(pkg)
        return {'status_code': 200, 'msg': 'Successfully deleted {} packages'.format(packages)}

    def batch_delete_filesystems(self, filesystems):
        if __OPERATION_MODE__ == DB_MODE:
            return self.batch_delete_filesystems_from_db(filesystems)
        for filesystem in filesystems:
            try:
                rmtree(os.path.join(self.root_dir, filesystem))
            except OSError as e:
                pass
                # do nothing in batch delete
                # raise Exception404('Invalid filesystem: {}'.format(str(e)))
        return {'status_code': 200, 'msg': 'Successfully deleted filesystems {}'.format(filesystems)}

    # from db
    def batch_delete_filesystems_from_db(self, filesystems):
        fs_service = FilesystemService()
        for fs_name in filesystems:
            fs = fs_service.get_filesystem_by_name(fs_name)
            fs_service.delete(fs)
        return {'status_code': 200, 'msg': 'Successfully deleted filesystems {}'.format(filesystems)}

    def batch_move_requests_to_test_case(self, filesystem, requests, to_test):
        requests = map(int, requests)
        to_test = int(to_test)
        if __OPERATION_MODE__ == DB_MODE:
            return self.batch_move_requests_to_test_case_from_db(filesystem, requests, to_test)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            PACKAGE_T = 'package'
            TEST_T = 'test'
            requests_queue = deque()
            requests_queue.append((filesystem_dict['packages'][0], PACKAGE_T))
            target_requests = []
            target_test = None
            while len(requests_queue) > 0:
                node, nodetype = requests_queue.popleft()
                if nodetype == PACKAGE_T:
                    for test in node["test_cases"]:
                        test_index = test["index"]
                        if test_index == to_test:
                            target_test = test
                        requests_queue.append((test, TEST_T))
                    for package in node["packages"]:
                        requests_queue.append((package, PACKAGE_T))
                if nodetype == TEST_T:
                    filtered_requests = filter(lambda request: request["index"] not in requests, node["requests"])
                    target_requests += filter(lambda request: request["index"] in requests, node["requests"])
                    node["requests"] = list(filtered_requests)
            if target_test is None:
                raise Exception404('Target test not found')
            target_test['requests'] += target_requests
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved {} requests'.format(requests)}

    # from db
    def batch_move_requests_to_test_case_from_db(self, filesystem_name, requests, to_test):
        service = RequestService()
        requests.reverse()
        for _id in requests:
            rq = service.get(_id)
            rq.test_case_id = to_test
            service.save(rq)
            service.refresh(rq)
            tc = rq.test_case
            tc.move_request_to_bottom(_id)
            service.save(tc)

        return {'status_code': 200, 'msg': 'Successfully moved {} requests'.format(requests)}

    def batch_move_test_cases_to_package(self, filesystem, tests, to_package):
        tests = map(int, tests)
        if __OPERATION_MODE__ == DB_MODE:
            return self.batch_move_test_cases_to_package_from_db(filesystem, tests, to_package)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            tests_queue = deque()
            tests_queue.append(filesystem_dict['packages'][0])
            target_tests = []
            while len(tests_queue) > 0:
                node = tests_queue.popleft()
                for package in node["packages"]:
                    tests_queue.append(package)
                filtered_tests = filter(lambda test: test["index"] not in tests, node["test_cases"])
                target_tests += filter(lambda test: test["index"] in tests, node["test_cases"])
                node["test_cases"] = list(filtered_tests)
            target_package = self.get_package(filesystem_dict, to_package)
            if target_package is None:
                raise Exception404('Could not find destination package')
            target_package["test_cases"] += target_tests
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully deleted {} test cases'.format(tests)}

    # from db
    def batch_move_test_cases_to_package_from_db(self, filesystem_name, tests, to_package):
        fs_service = FilesystemService()
        fs = fs_service.get_filesystem_by_name(filesystem_name)
        package = fs.get_package_by_path(to_package)
        pkg_id = package.id
        tc_service = TestCaseService()
        tests.reverse()
        for _id in tests:
            tc = tc_service.get(_id)
            tc.package_id = pkg_id
            tc_service.save(tc)
            tc_service.refresh(tc)
            tc.package.move_test_case_to_bottom(tc.id)
            tc_service.save(tc)
        return {'status_code': 200, 'msg': 'Successfully moved test cases {} to package {}'.format(tests, to_package)}

    def batch_move_packages_to_package(self, filesystem, packages, to_package):
        if __OPERATION_MODE__ == DB_MODE:
            return self.batch_move_packages_to_package_from_db(filesystem, packages, to_package)
        TO_BE_MOVED_FLAG = '___TO_BE_MOVED___'
        packages = map(lambda pack: pack.strip('/'), packages)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            packages_queue = deque()
            packages_queue.append((filesystem_dict['packages'][0], ''))
            target_packages = []
            while len(packages_queue) > 0:
                node, parent_name = packages_queue.popleft()
                node_name = node["dir"]
                package_name = parent_name + node_name
                for package in node["packages"]:
                    child_package_name = package_name + '/' + package['dir']
                    print(child_package_name)
                    print(packages)
                    print(child_package_name in packages)
                    if child_package_name in packages:
                        package[TO_BE_MOVED_FLAG] = True
                    else:
                        packages_queue.append((package, package_name + '/'))
                target_packages += filter(lambda pack: pack.get(TO_BE_MOVED_FLAG, False), node["packages"])
                node["packages"] = filter(lambda pack: not pack.get(TO_BE_MOVED_FLAG, False), node["packages"])
                for package in target_packages:
                    package.pop(TO_BE_MOVED_FLAG, None)
            target_parent_package = self.get_package(filesystem_dict, to_package)
            if target_parent_package is None:
                raise Exception400('Malformed selection')
            for package in target_packages:
                package_name = package["dir"]
                if not self.__is_unique_package_name(target_parent_package, package_name):
                    counter = self.last_ambiguous_package(target_parent_package, package_name)
                    package["dir"] = self.append_counter_to_name(package_name, counter)
                target_parent_package["packages"].append(package)

            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved {} packages'.format(packages)}

    # from db
    def batch_move_packages_to_package_from_db(self, filesystem_name, packages, to_package):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        packages.reverse()
        parent = filesystem.get_package_by_path(to_package)
        packages.reverse()
        for pkg_path in packages:
            pkg = filesystem.get_package_by_path(pkg_path)
            if pkg.is_root():
                continue
            if pkg.has_child(parent):
                continue
            if parent.has_child_by_name(pkg.dir):
                continue
            pkg.parent_package_id = parent.id
            fs_service.save(pkg)
            fs_service.refresh(pkg)
            pkg.parent.move_package_to_bottom(pkg.id)
            fs_service.save(pkg)
        return {'status_code': 200, 'msg': 'Successfully moved {} packages'.format(packages)}

    def __is_unique_package_name(self, parent_package, package_name):
        for package in parent_package["packages"]:
            if package["dir"] == package_name:
                return False
        return True

    def append_counter_to_name(self, name, counter):
        pattern = r'^.+\((\d+)\)$'
        match = re.match(pattern, name)
        if match:
            return '('.join(name.split('(')[:-1]) + '({})'.format(counter)
        return name + '({})'.format(counter)

    def last_ambiguous_package(self, parent_package, name):
        if re.match(r'^.+\(\d+\)$', name):
            name = '('.join(name.split('(')[:-1])
        name = name.replace('(', '\(').replace(')', '\)')
        pattern = r'^{}\((\d+)\)$'.format(name)
        print(pattern)
        counter = 0
        for package in parent_package["packages"]:
            package_name = package["dir"]
            match = re.match(pattern, package_name)
            if match:
                counter = max(int(match.group(1)), counter)
        return counter + 1

    def move_request_down(self, filesystem, package_path, test_no, request_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_request_down_from_db(filesystem, package_path, test_no, request_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            test_no = int(test_no)
            request_no = int(request_no)
            if test_no < 0:
                raise Exception404('Test no can\'t be lower than 0')
            requests = test_cases[test_no]['requests']
            if request_no == len(requests) - 1:
                raise Exception400("Can't move request any lower")
            if request_no < 0:
                raise Exception400('Request no can\'t be lower than 0')
            try:
                upper = requests[request_no]
                lower = requests[request_no + 1]
                requests[request_no + 1], requests[request_no] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved request down.'}

    def move_request_up(self, filesystem, package_path, test_no, request_no):
        if __OPERATION_MODE__ == DB_MODE:
            return self.move_request_up_from_db(filesystem, package_path, test_no, request_no)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            test_no = int(test_no)
            request_no = int(request_no)
            if test_no < 0:
                raise Exception404('Test no can\'t be lower than 0')
            requests = test_cases[test_no]['requests']
            if request_no == 0:
                raise Exception400("Can't move request any higher")
            if request_no < 0:
                raise Exception400('Request no can\'t be lower than 0')
            try:
                upper = requests[request_no - 1]
                lower = requests[request_no]
                requests[request_no], requests[request_no - 1] = upper, lower
            except IndexError as e:
                raise Exception400(str(e))
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully moved request up.'}

    # from db
    def move_request_up_from_db(self, filesystem_name, package_path, test_no, request_no):
        request_no = int(request_no)
        test_no = int(test_no)
        if request_no == 0:
            raise Exception400("Can't move request any higher")
        if request_no < 0:
            raise Exception400('Request no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_test_case = filesystem.get_test_case_by_index(package_path, test_no)
        if request_no >= len(parent_test_case.requests):
            raise Exception400('Request index out of bound')
        upper_request = parent_test_case.requests[request_no - 1]
        lower_request = parent_test_case.requests[request_no]
        upper_request.execution_order, lower_request.execution_order = lower_request.execution_order, upper_request.execution_order
        fs_service.save(upper_request)
        fs_service.save(lower_request)
        return {'status_code': 200, 'msg': 'Successfully moved request up.'}

    # from db
    def move_request_down_from_db(self, filesystem_name, package_path, test_no, request_no):
        request_no = int(request_no)
        test_no = int(test_no)
        if request_no < 0:
            raise Exception400('Request no can\'t be lower than 0')
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        parent_test_case = filesystem.get_test_case_by_index(package_path, test_no)
        if request_no >= len(parent_test_case.requests):
            raise Exception400('Request index out of bound')
        if request_no == len(parent_test_case.requests) - 1:
            raise Exception400("Can't move request any lower")
        upper_request = parent_test_case.requests[request_no]
        lower_request = parent_test_case.requests[request_no + 1]
        upper_request.execution_order, lower_request.execution_order = lower_request.execution_order, upper_request.execution_order
        fs_service.save(upper_request)
        fs_service.save(lower_request)
        return {'status_code': 200, 'msg': 'Successfully moved request down.'}

    def rename_request(self, filesystem, package_path, test_no, request_no, request_name):
        if __OPERATION_MODE__ == DB_MODE:
            return self.rename_request_from_db(filesystem, package_path, test_no, request_no, request_name)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            test_cases = package['test_cases']
            target_test_case = test_cases[int(test_no)]
            requests = target_test_case['requests']
            requests[int(request_no)]['name'] = request_name
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully renamed request as {}'.format(request_name)}

    # from db
    def rename_request_from_db(self, filesystem_name, package_path, test_no, request_no, request_name):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        try:
            package = filesystem.get_package_by_path(package_path)
        except:
            raise Exception404('Package not found')
        try:
            target_test_case = package.test_cases[int(test_no)]
        except:
            raise Exception404('Test case not found')
        try:
            target_request = target_test_case.requests[int(request_no)].raw_request
        except:
            raise Exception404('Request not found')
        target_request.name = request_name
        fs_service.save(target_request)
        return {'status_code': 200, 'msg': 'Successfully renamed request as {}'.format(request_name)}

    def create_test_case(self, filesystem, package_path, test_name):
        if __OPERATION_MODE__ == DB_MODE:
            return self.create_test_case_from_db(filesystem, package_path, test_name)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Parent package not found')
            test_cases = package['test_cases']
            test_cases.append({
                'requests': [],
                'name': test_name,
                'selected': False,
            })
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
        return {'status_code': 200, 'msg': 'Successfully created test case {}'.format(test_name)}

    # from db
    def create_test_case_from_db(self, filesystem_name, package_path, test_name):
        test_name = test_name.replace('/', '_')
        service = FilesystemService()
        filesystem = service.get_filesystem_by_name(filesystem_name)
        parent_package = filesystem.get_package_by_path(package_path)
        if not parent_package:
            raise Exception404('Parent package not found')
        test_case_service = TestCaseService()
        test_case_service.create_test_case(test_name, parent_package.id)
        return {'status_code': 200, 'msg': 'Successfully created test case {}'.format(test_name)}

    def select_package(self, filesystem, package_path, package_selected):
        if __OPERATION_MODE__ == DB_MODE:
            return self.select_package_from_db(filesystem, package_path, package_selected)
        filesystem_path = os.path.join(self.root_dir, filesystem, 'filesystem.json')
        with open(filesystem_path, 'r+') as filesystem_file:
            filesystem_dict = json.load(filesystem_file)
            package = self.get_package(filesystem_dict, package_path)
            if not package:
                raise Exception404('Package not found')
            package['selected'] = bool(package_selected)
            filesystem_file.seek(0)
            json.dump(filesystem_dict, filesystem_file, indent=4)
            filesystem_file.truncate()
            return {'status_code': 200, 'msg': 'Successfully set package {}'.format(bool(package_selected))}

    # from db
    def select_package_from_db(self, filesystem_name, package_path, package_selected):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        package = filesystem.get_package_by_path(package_path)
        package.selected = bool(package_selected)
        fs_service.save(package)
        return {'status_code': 200, 'msg': 'Successfully set package {}'.format(bool(package_selected))}

    def delete_filesystem(self, filesystem):
        if __OPERATION_MODE__ == DB_MODE:
            return self.delete_filesystem_from_db(filesystem)
        try:
            rmtree(os.path.join(self.root_dir, filesystem))
        except OSError as e:
            raise Exception404('Invalid filesystem: {}'.format(str(e)))
        return {'status_code': 200, 'msg': 'Successfully deleted filesystem {}'.format(filesystem)}

    # from db
    def delete_filesystem_from_db(self, filesystem_name):
        fs_service = FilesystemService()
        filesystem = fs_service.get_filesystem_by_name(filesystem_name)
        fs_service.delete(filesystem)
        return {
            'status_code': 200,
            'msg': 'Successfully deleted Filesystem',
        }


    def save_credential(self, app_name, client_id, client_secret):
        options_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'options.json')
        with open(options_file_path, 'r+') as options_file:
            options = json.load(options_file)
            options['client_id'] = client_id
            options['client_secret'] = client_secret
            options['appname'] = app_name
            options_file.seek(0)
            options_file.write(json.dumps(options))
            options_file.truncate()
        return 'Successfully set credential'

    def get_credential(self):
        options_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'options.json')
        with open(options_file_path, 'r') as options_file:
            return options_file.read()

class ThreadedHTTPServer(ThreadingMixIn, WSGIServer):
    """Handle requests in a separate thread."""


def make_server(host, port, app, server_class=ThreadedHTTPServer, handler_class=WSGIRequestHandler):
    """Create a new WSGI server listening on 'host' and 'port' for 'app'."""
    server = server_class((host, port), handler_class)
    server.set_app(app)
    return server


def start_server(root_path, port=8965):
    # root_path = "/temp"
    # Configure hostname and port on which the server will listen
    # hostname = "127.0.0.1" # Use empty string for localhost (local access only)
    hostname = ""  # Use empty string for 0.0.0.0 (allows remote access)
    wsgi_app = FancyTreeWsgiApp({"root_path": root_path})
    httpd = make_server(hostname, int(port), wsgi_app, server_class=WSGIServer)
    sa = httpd.socket.getsockname()
    print("Exporting file system at ", root_path, " for fancytree.")
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    if __OPERATION_MODE__ == FILE_MODE:
        if not os.path.isdir(root_path):
            os.makedirs(root_path)

    httpd.serve_forever()


if __name__ == "__main__":
    try:
        root__path = sys.argv[1]
    except:
        root__path = os.path.join(os.path.abspath(__file__), 'default_root')

    if __OPERATION_MODE__ == FILE_MODE:
        if not os.path.isdir(root__path):
            os.makedirs(root__path)

    try:
        port = int(sys.argv[2])
    except:
        port = 8965

    start_server(root__path, port)
