import logging
from pyramid.httpexceptions import HTTPNoContent, HTTPMethodNotAllowed, HTTPBadRequest

log = logging.getLogger(__name__)


class APIBase(object):
    """
    Better Base class for all the API implementation classes. Handles stuff like:

    * Allowing CORS requests
    * Returning proper response to HTTP OPTIONS method. This is requested by all modern
      browsers when making XHR calls.

    :param _HTTP_ALLOWED_METHODS: (List) specified the HTTP methods the current class
                                  implementing an API endpoint supports
    """

    _ENDPOINTS = {
        'GET': [
            # (endpoint, method_to_call),
        ]
    }

    def __init__(self, request):
        self.request = request
        self.endpoint_info = {}
        self.request_params = None

    def _cors_headers(self):
        return {
            'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json; charset=utf-8',
            "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
            "Access-Control-Allow-Methods": ",".join(self._ENDPOINTS.keys())
        }

    def _match_endpoint(self, ep):

        request_ep = self.request.matchdict['endpoint']
        endpoint_to_match = ep[0]

        if 0 == len(request_ep) and '' == endpoint_to_match:
            self.endpoint_info = {}
            return True

        if endpoint_to_match != '':
            ep_parts = endpoint_to_match.split('/')

            if len(request_ep) == len(ep_parts):
                # Both have same number of url slash fragments, lets see if the non {} fragments match

                for i in range(len(ep_parts)):

                    if ep_parts[i].startswith('{') and ep_parts[i].endswith('}'):
                        k = ep_parts[i][1:-1]
                        self.endpoint_info[k] = request_ep[i]

                    elif ep_parts[i] != request_ep[i]:
                        self.endpoint_info = {}
                        return False

                return True

        return False

    def handle_request(self):

        if 'OPTIONS' == self.request.method:
            raise HTTPNoContent(headers=self._cors_headers())

        if self.request.method not in self._ENDPOINTS.keys():
            raise HTTPMethodNotAllowed(
                'HTTP {} method is not supported by this API endpoint'.format(
                    self.request.method))

        # parse endpoint
        for ep in self._ENDPOINTS[self.request.method]:
            if self._match_endpoint(ep):
                if hasattr(self, ep[1]) and callable(getattr(self, ep[1])):
                    self.request.response.headers.update(self._cors_headers())
                    return getattr(self, ep[1])()

        # No endpoints matched, return Bad Request
        raise HTTPBadRequest()
