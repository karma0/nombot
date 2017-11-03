"""
API Core
"""

from multiprocessing import Process
import sched
import time

from app.log import LoggerMixin
from common.factory import Creator
from api.websock import SockChannel  # pylint: disable=import-error,no-name-in-module


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
        print(f"SHUTDOWN: {len(self.apis)}")
        for wsock in self.wsocks:
            wsock.shutdown()
        for api in self.apis:
            api.shutdown()


class ApiProduct:
    """ApiAdapterFactory Product interface"""
    thread = None
    keep_going = True

    def __init__(self):
        self.api = None
        self.context = None
        self.callback = None

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.context = context
        self.callback = self.context.get("callback")

    def shutdown(self):
        """Executed on shutdown of application"""
        self.keep_going = False
        if hasattr(self.api, "shutdown"):
            self.api.shutdown()


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
                SockChannel(self.api, channel, res_type, self.callback)
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
        self.context["inst"] = self  # This adapter can be used by strategies

        def loop():
            """Loop on scheduler, calling calls"""
            while self.keep_going:
                for call, calldata in self.context.get("calls", {}).items():
                    self.call(call, **calldata)
                self.scheduler.run()

        self.thread = Process(target=loop)
        self.thread.start()

    def call(self, callname, arguments=None, delay=None, priority=None):
        """Executed on each scheduled iteration"""
        # Setup scheduler arguments
        sched_args = {}  # type: dict
        if delay is not None:
            sched_args["delay"] = delay
        if priority is not None:
            sched_args["priority"] = priority

        # See if a method override exists
        action = getattr(self.api, callname, None)

        # Define a mock method if one doesn't exist
        def mthd(*args):
            """Call the API and generate the result for self.callback"""
            if not callable(action):
                return self.generate_result(
                    callname, self.api.call(callname, *args))
            return self.generate_result(callname, action(*args))

        # Schedule the call, generating results upon completion
        if sched_args:
            sched_args["action"] = mthd
            if arguments is not None:
                sched_args["arguments"] = arguments
            self.scheduler.enter(**sched_args)

        else:
            if arguments is not None:
                mthd(*arguments)
            else:
                mthd()

    def generate_result(self, callname, result):
        """Generate a results object for delivery to the context object"""
        # Retrieve path from API class
        try:
            schema = self.api.result_schema()
            schema.context['callname'] = callname
            self.callback(schema.dump(result).data, self.context)
        except:  # NOQA
            raise Exception(f"""Could not parse response for {callname}; data:
            {result}""")
