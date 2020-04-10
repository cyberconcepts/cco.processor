#
# cco.processor.hook
#

"""
Mixin classes and other stuff for hooking into loops (Zope3, Bluebream)
objects so that certain operations (like setting and retrieving attributes)
can be handled by services like storage or notifiers.
"""

from logging import getLogger
import traceback
import transaction

from cco.processor.common import _not_found

from loops import common

logger = getLogger('cco.processor.hook')

loader_hooks = {}
processor_hooks = {}


def loadData(obj):
    #print 'loadData ***', obj.context.__name__
    data = {}
    for hook in obj._hook_loaders:
        fct = loader_hooks.get(hook)
        try:
            fct(obj, data)
        except:
            logger.error(traceback.format_exc())
    return data


def processData(obj, data):
    #print 'processData ***', obj.context.__name__
    for hook in obj._hook_processors:
        fct = processor_hooks.get(hook)
        try:
            fct(obj, data)
        except:
            logger.error(traceback.format_exc())        


class AdapterBase(common.AdapterBase):

    _hook_message_base = 'cco/data/dummy'
    _hook_loaders = []
    _hook_processors = []
    _hook_config = {}

    _old_data = None
    _cont = None
    _id = None

    def __init__(self, context):
        super(AdapterBase, self).__init__(context)
        object.__setattr__(self, '_new_data', {})

    def __getattr__(self, attr):
        value = self._new_data.get(attr, _not_found)
        if value is _not_found:
            if self._old_data is None:
                object.__setattr__(self, '_old_data', loadData(self))
            value = self._old_data.get(attr, _not_found)
        if value is _not_found:
            value = super(AdapterBase, self).__getattr__(attr)
            self._old_data[attr] = value
        return value

    def __setattr__(self, attr, value):
        super(AdapterBase, self).__setattr__(attr, value)
        if attr.startswith('__') or attr in self._adapterAttributes:
            return
        if not self._new_data:
            tr = transaction.manager.get()
            tr.addBeforeCommitHook(processData, [self, self._new_data], {})
        self._new_data[attr] = value
