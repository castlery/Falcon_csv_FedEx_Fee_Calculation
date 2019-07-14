import falcon

from .fee import Resource


api = application = falcon.API()

fee = Resource()
api.add_route('/fee', fee)