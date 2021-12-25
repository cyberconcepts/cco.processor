#
# cco.processor.storage
#

from logging import getLogger
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.traversing.api import getName

from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.setup import addAndConfigureObject
from loops import util

from cco.processor.common import Error, _invalid

logger = getLogger('cco.processor.storage')


# check attributes, collect changes

def check_change(obj, attr, newValue, includeOnly=None, omit=[], updateEmpty=[]):
    if attr.startswith('_') or attr in omit or newValue in (_invalid, None):
        return None
    if includeOnly is not None and attr not in includeOnly:
        return None
    oldValue = None
    if obj is not None: # called from create_object
        oldValue = getattr(obj, attr)
    if isinstance(newValue, list) and oldValue:
        oldValue = list(oldValue)
    if newValue == oldValue or (oldValue and attr in updateEmpty):
        return None
    return (attr, (oldValue, newValue))

def collect_changes(obj, data, includeOnly=None, omit=[], updateEmpty=[]):
    changes = [check_change(obj, attr, newValue, includeOnly, omit, updateEmpty)
        for attr, newValue in data.items()]
    return dict(c for c in changes if c is not None)

# access to persistent objects

def create_or_update_object(context, type_name, data, 
        includeOnly=None, omit=[], updateEmpty=[], dryRun=False):
    obj = get_object(context, type_name, data)
    if obj is None:
        return create_object(context, type_name, data, includeOnly, omit, updateEmpty, dryRun)
    else:
        return update_object(obj, data, includeOnly, omit, updateEmpty, dryRun)

def create_object(context, type_name, data,
        includeOnly=None, omit=[], updateEmpty=[], dryRun=False):
    logCreate = data.get('_log_create', True)
    ident = data.get('_identifier')
    if logCreate:
        logger.info('create_object %s %s: %s' % (type_name, ident, data))
    changes = collect_changes(None, data, includeOnly, omit, updateEmpty)
    msg = {'action': 'create', 'identifier': ident, 'changes': changes}
    if dryRun:
        return msg
    type = adapted(context['concepts'][type_name])
    cont = type.conceptManager or 'concepts'
    name = (type.namePrefix or (type_name + '.')) + ident
    attrs = {}
    for attr, (ov, val) in changes.items():
        if isinstance(val, Error):
            logger.warn('create_object error: %s: %s %s' % (ident, attr, val))
            msg['info'] = 'error'
            return msg
        attrs[attr] = val
    obj = addAndConfigureObject(context[cont], Concept, name, 
        conceptType=baseObject(type), **attrs)
    msg['uid'] = util.getUidForObject(obj)
    return msg

def update_object(obj, data, includeOnly=None, omit=[], updateEmpty=[], dryRun=False):
    logUpdate = data.get('_log_update', True)
    ident = (data.get('_identifier') or 
                getattr(obj, 'identifier', getName(baseObject(obj))))
    changes = collect_changes(obj, data, includeOnly, omit, updateEmpty)
    msg = {'action': 'update', 'identifier': ident, 'uid': obj.uid, 'changes': changes}
    if logUpdate and changes:
        logger.info('update_object %s: %s' % (ident, changes))
    if dryRun:
        return msg
    for attr, (ov, nv) in changes.items():
        if isinstance(nv, Error):
            logger.warn('update_object error: %s: %s %s' % (ident, attr, nv))
            msg['info'] = 'error'
            return msg
        setattr(obj, attr, nv)
    if changes: 
        notify(ObjectModifiedEvent(baseObject(obj)))
    return msg

def get_object(context, type_name, data):
    if context is None:
        logger.error('get_object %s: context not set, data: %s' % (type_name, data))
    ident = data.get('_identifier')
    if ident is None:
        logger.warn('get_object %s: _identifier missing: %s' % (type_name, data))
    type = adapted(context['concepts'][type_name])
    cont = type.conceptManager or 'concepts'
    name = (type.namePrefix or (type_name + '.')) + ident
    ob = context[cont].get(name)
    if ob:
        return adapted(ob)
    return None

