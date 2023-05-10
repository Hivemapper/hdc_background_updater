class Response:
    def __init__(self, code, json):
        self.code = code
        self.json = json


class SuccessResonse(Response):
    def __init__(self):
        Response.__init__(self, 200, '{"response": "success"}')


class ErrorResponse(Response):
    def __init__(self, code, error_string):
        Response.__init__(self, code, f'{{"response": "{error_string}"}}')


class BadRouteResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 500, "bad route")


class NoVersionResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 500, "no version found")


class InvalidUpdateStateResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 403, "invalid state for update")


class InvalidCancelStateResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 403, "invalid state for cancel")


class InvalidRevertStateResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 403, "invalid state for revert")


class NoDataResponse(ErrorResponse):
    def __init__(self):
        ErrorResponse.__init__(self, 400, "no data provided")
