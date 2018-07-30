from pyramid.view import view_defaults, view_config

from .api_base import APIBase


@view_defaults(route_name='schedules_api', renderer="prettyjson")
class SchedulerAPI(APIBase):

    _ENDPOINTS = {
        'GET': [
            ('', 'get_schedules')
        ],
        'PUT': [
            ('', 'set_schedules')
        ]
    }

    @view_config(request_method=("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"))
    def request_handler(self):
        return self.handle_request()

    def get_schedules(self):
        print("get_schedules called!")
        return {}

    def set_schedules(self):

        print("set_schedules called!")
        self.request.response.status_code = 200

        return self.request.response
