"""
API Core
"""

from core.log import LoggerMixin
from common.factory import Creator
from api.websock import SockChannel
from api.schema import REQUEST_MAP, RESPONSE_MAP, ResponseSchema


class WsAdapterFactory(Creator):  # pylint: disable=too-few-public-methods
    """Generator of WsAdapters"""
    def _factory_method(self):
        return WsAdapter()


class ApiAdapterFactory(Creator):  # pylint: disable=too-few-public-methods
    """Generator of ApiAdapters"""
    def _factory_method(self):
        return ApiAdapter()


class ApiMetaAdapter(LoggerMixin):
    """Adapter of adapters for all API instantiations"""
    name = "api"

    def __init__(self, api_contexts):
        self.apis = []  # type: list
        self.wsocks = []  # type: list

        self.create_logger()

        self.log.debug(f"Launching API contexts: {api_contexts}")
        for name, context in api_contexts.items():
            #wsock = WsAdapterFactory()
            #wsock.product.interface(context)
            #self.wsocks.append(wsock.product)

            self.log.debug(f"Starting API: {name}")
            api = ApiAdapterFactory()
            api.product.interface(context)
            self.apis.append(api.product)

    def run(self):
        """Executed on startup of application"""
        for wsock in self.wsocks:
            wsock.run(wsock.api_context.get("callback"))
        for api in self.apis:
            api.run()

    def shutdown(self):
        """Executed on shutdown of application"""
        for wsock in self.wsocks:
            wsock.run()
        for api in self.apis:
            api.shutdown()


class ApiProduct:
    """ApiAdapterFactory Product interface"""
    def __init__(self):
        self.api = None
        self.api_context = None

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.api = None
        self.api_context = context

    def shutdown(self):
        """Executed on shutdown of application"""
        self.api.shutdown()


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    def run(self):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api = self.api_context.get("cls")(self.api_context)

        # Initialize websocket with channels
        self.api.connect_ws(self.api.on_ws_connect, [
            SockChannel(channel, res_type, self.api_context.get("callback"))
            for channel, res_type in
            self
            .api_context
            .get("conf")
            .get("subscriptions")(self.api_context.get("name")).items()
        ])


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    def run(self):
        """Executed on startup of application"""
        self.api = self.api_context.get("cls")(self.api_context)

        # TODO: schedule loop
        self.api_context.get("callback")(
            {call: self.call(call) for call in
             self.api_context.get("calls")}
            )

    def call(self, call):
        """Executed on each scheduled iteration"""
        method = getattr(self.api, call, None)
        if callable(method):
            return self.generate_result(method(), call)
        return self.generate_result(self.api.call(call), call)

    def generate_result(self, result, callname):
        """Generate a results object for delivery to the context object"""
        # Retrieve path from API class
        try:
            resp_sch = self.api.result_schema.load(result)
        except:
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {resp_sch["errors"]}""")
        print(f"""RESP_SCH!{resp_sch.data["data"]}""")
        # TODO: Leave this up to the Coinigy API
        try:
            loaded_sch = RESPONSE_MAP.get(callname).load(resp_sch.data["data"])
            return loaded_sch.data
        except:
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {loaded_sch["errors"]}""")
