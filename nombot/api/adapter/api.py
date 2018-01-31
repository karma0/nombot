"""
API Core
"""

from multiprocessing import Process
import sched
import time

from nombot.api.product import ApiProduct  # pylint: disable=E0611,E0401


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    scheduler = sched.scheduler(time.time, time.sleep)
    keep_going = True
    is_connected_ws = False

    api = None
    thread = None

    def run(self):
        """Executed on startup of application"""
        self.api = self.context.get("cls")(self.context)
        self.context["inst"].append(self)  # Adapters used by strategies

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
        if action is None:
            try:
                action = self.api.ENDPOINT_OVERRIDES.get(callname, None)
            except AttributeError:
                action = callname
        if action is not None:
            self.api.log.debug(
                f"Using API's override for /{callname}: /{action}")

        # Define a mock method if one doesn't exist
        def mthd(args=None):
            """Call the API and generate the result for self.callback"""
            if not callable(action):
                request = self._generate_request(action, args)
                if action is None:
                    return self._generate_result(
                        callname, self.api.call(callname, args))
                return self._generate_result(
                    callname, self.api.call(action, args))
            request = self._generate_request(callname, args)
            return self._generate_result(callname, action(request))

        # Schedule the call, generating results upon completion
        if sched_args:
            sched_args["action"] = mthd
            if arguments is not None:
                sched_args["argument"] = (arguments,)
            self.scheduler.enter(**sched_args)

        else:
            if arguments is not None:
                mthd(arguments)
            else:
                mthd()

    def _generate_request(self, callname, request):
        """Generate a request object for delivery to the API"""
        # Retrieve path from API class
        schema = self.api.request_schema()
        schema.context['callname'] = callname
        return schema.dump(request).data.get("payload")

    def _generate_result(self, callname, result):
        """Generate a results object for delivery to the context object"""
        # Retrieve path from API class
        schema = self.api.result_schema()
        schema.context['callname'] = callname
        self.callback(schema.load(result), self.context)
