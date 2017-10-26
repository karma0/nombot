"""
API Core
"""

from multiprocessing import Process

from app.log import LoggerMixin
from common.factory import Creator
from api.websock import SockChannel


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

    def __init__(self, contexts):
        self.apis = []  # type: list
        self.wsocks = []  # type: list

        self.create_logger()

        for name, context in contexts.items():
            wsock = WsAdapterFactory()
            wsock.product.interface(context)
            self.wsocks.append(wsock.product)

            self.log.debug(f"Starting API: {name}")
            api = ApiAdapterFactory()
            api.product.interface(context)
            self.apis.append(api.product)

    def run(self):
        """Executed on startup of application"""
        for wsock in self.wsocks:
            wsock.run()
        for api in self.apis:
            api.run()

    def shutdown(self):
        """Executed on shutdown of application"""
        # TODO: Look into this vs. trap
        for wsock in self.wsocks:
            wsock.shutdown()
        for api in self.apis:
            api.shutdown()


class ApiProduct:
    """ApiAdapterFactory Product interface"""
    def __init__(self):
        self.api = None
        self.context = None

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.context = context

    def shutdown(self):
        """Executed on shutdown of application"""
        self.api.shutdown()


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    thread = None

    def run(self):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api = self.context.get("cls")(self.context)

        # Initialize websocket in a thread with channels
        self.thread = Process(target=self.api.connect_ws, args=(
            self.api.on_ws_connect, [
                SockChannel(channel, res_type, self.context.get("callback"))
                for channel, res_type in
                self
                .context
                .get("conf")
                .get("subscriptions").items()
            ]))
        self.thread.start()

    def shutdown(self):
        """Executed on shutdown of websockets"""
        self.thread.join()


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    def run(self):
        """Executed on startup of application"""
        self.api = self.context.get("cls")(self.context)

        # TODO: schedule loop
        self.context.get("callback")(
            {call: self.call(call) for call in
             self.context.get("calls")},
            self.context
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
            schema = self.api.result_schema()
            schema.context['callname'] = callname
            resp_sch = schema.load(result)
        except:  # NOQA
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {resp_sch["errors"]}""")
        return resp_sch
