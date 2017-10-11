"""
Context for passing through middleware modules
"""


class Context:
    """
    Context for middleware pipeline
    """
    pass


def build_context(apicalls):
    """Assemble and return a context"""
    ctx = Context()
    for call in apicalls.keys():
        ctx.__setattr__(call, apicalls[call])
