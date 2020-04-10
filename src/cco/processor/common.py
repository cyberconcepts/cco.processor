#
# cco.processor.common
#

"""
Common stuff for the cco.processor package
"""


class Error(object):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '<Error %r>' % self.message

    __repr__ = __str__

def error(msg):
    return Error(msg)

_not_found = object()
_invalid = object()


