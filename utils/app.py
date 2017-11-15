"""Application for api services."""

import os

import falcon
import ujson
from model import predict

VERSION = os.getenv("MODEL_VERSION", None)


class Index:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_405

    def on_post(self, req, resp):

        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                'Error',
                ex.message,
            )

        try:
            result_json = ujson.loads(raw_json.decode())
        except ValueError:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The '
                'JSON was incorrect.'
            )

        output = predict(result_json)

        resp.body = ujson.dumps({
            'output': output,
            'version': VERSION
        })


api = falcon.API()
api.add_route('/', Index())
