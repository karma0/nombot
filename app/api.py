"""
API Core
"""

from multiprocessing import Process
import sched
import time

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
    thread = None

    def __init__(self):
        self.api = None
        self.context = None

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.context = context
        self.callback = self.context.get("callback")

    def shutdown(self):
        """Executed on shutdown of application"""
        self.keep_going = False
        self.api.shutdown()
        self.thread.join()


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    def run(self):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api = self.context.get("cls")(self.context)

        # Initialize websocket in a thread with channels
        self.thread = Process(target=self.api.connect_ws, args=(
            self.api.on_ws_connect, [
                SockChannel(channel, res_type, self.callback)
                for channel, res_type in
                self
                .context
                .get("conf")
                .get("subscriptions").items()
            ]))
        self.thread.start()


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    scheduler = sched.scheduler(time.time, time.sleep)
    keep_going = True

    def run(self):
        """Executed on startup of application"""
        self.api = self.context.get("cls")(self.context)
        self.context["inst"] = self # This adapter can be used by strategies

        """Loop on scheduler, calling calls"""
        def loop():
            while self.keep_going:
                for call, calldata in self.context.get("calls", {}).items():
                    self.call(call, **calldata)
                self.scheduler.run()

        self.thread = Process(target=loop)
        self.thread.start()

    def call(self, call, arguments=None, rate=None, priority=None):
        """Executed on each scheduled iteration"""
        # See if a method override exists
        method = getattr(self.api, call, None)

        # Define a mock method if one doesn't exist
        def mthd(call, *args):
            return self.api.call(call, *args)

        if not callable(method):
            method = mthd

        # Setup scheduler arguments
        sched_args = {}  # type: dict
        if not rate is None:
            sched_args["rate"] = rate
        if not priority is None:
            sched_args["priority"] = priority

        # Schedule the call, generating results upon completion
        return self.generate_result(method, arguments, call, sched_args)

    def generate_result(self, method, arguments, callname, sched_args):
        """Generate a results object for delivery to the context object"""
        # schedule api call
        if sched_args:
            self.callback(method(arguments))
        else:
            self.callback(method(arguments))

        # Retrieve path from API class
        try:
            schema = self.api.result_schema()
            schema.context['callname'] = callname
            resp_sch = schema.load(result)
        except:  # NOQA
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {resp_sch["errors"]}""")
        return resp_sch

        # self.
        # {call: self.call(call, **call) for call in
        # self.context.get("calls")},
        # self.context
        # )
