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

    @view_config(request_method=(
        "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"))
    def request_handler(self):
        # print(self.request)
        return self.handle_request()

    def get_schedules(self):
        print("get_schedules called!")
        schedules = {
            'add-every-5-seconds': {
                'task': 'beatrest.debug.debug_print',
                'type': 'interval',
                'value': 5.0,
                'args': ('hello from celery', ),
                'options': {'queue': 'tr', 'routing_key': 'tr'}
            },
            # 'print-msg-every-5-seconds': {
            #     'task': 'print',
            #     'type': 'interval',
            #     'value': 5.0,
            #     'args': ('hello from celery', ),
            #     'options': {'queue': 'tr', 'routing_key': 'tr'}
            # },
            'run-every-minute': {
                'task': 'beatrest.debug.file_debug',
                'type': 'crontab',
                'value': {'minute': '*'},  # run every minute
                'args': ('/tmp/beatrest_messages.txt', 'hello from crontab'),
                'last_run_at': '2018-10-01T14:43:56.812202',
                'options': {'queue': 'tr', 'routing_key': 'tr'}
            }
        }

        return schedules

    def set_schedules(self):

        print("set_schedules called!")
        self.request.response.status_code = 200

        return self.request.response
