"""
Context for passing through middleware modules
"""

from api.result_types import RESULT_TYPES


class Context(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def build_context(api_call_results):
    """Assemble and return a context"""
    #ctx = namedtuple(  # empty class accompishes similar

    # Ingest results, building a context object
    #ctx.__dict__.update(api_call_results)

    #print(f"RES: {api_call_results}")
    #for call, result in api_call_results.items():
    #    setattr(ctx, call, result)
    #    ctx.__setattr__(call, result)

    return Context(api_call_results)
