from lib.events import EventMixin
from browser import html
from .expobserver import ExpObserver
from .expression import ET_INTERPOLATED_STRING, parse
from .context import Context

from lib.logger import Logger
logger = Logger(__name__)

import re

class AttrDict(object):
    """
        A nicer interface to element attributes. Except for elements in exclude,
        the attribute values will be interpolated (provided they contain '{{').
        It has a dict-like interface which allows getting attr values and
        setting non-interpolated attributes.
        Any new attributes which are set will not be interpolated.
    """
    def __init__(self,element,exclude=[]):
        self._attrs = {}
        self._elem = element
        self._exclude = exclude
        for a in self._elem.attributes:
            if not a.name in exclude and '{{' in a.value:
                observer = ExpObserver(a.value,ET_INTERPOLATED_STRING)
                observer.bind('change',self._change_chandler)
                observer._attr=a
                self._attrs[a.name] = observer
            else:
                self._attrs[a.name] = a
        self._bound = False

    def bind_ctx(self,context):
        self._bound = True
        for attr in self._attrs.values():
            if isinstance(attr,ExpObserver):
                attr.watch(context)
                attr.evaluate()
                attr._attr.value = attr.value

    def _change_chandler(self,event):
        event.data['observer']._attr.value = event.data['new']

    def __iter__(self):
        return iter(self._attrs)

    def keys(self):
        return self._attrs.keys()

    def __getitem__(self, key):
        if self._bound:
            return self._attrs[key].value
        else:
            a = self._attrs[key]
            if isinstance(a, ExpObserver):
                return a._exp_src
            else:
                return a.value

    def __setitem__(self, key, value):
        if key in self._attrs:
            try:
                self._attrs[key].value = value
            except:
                pass
        else:
            if key not in self._exclude:
                setattr(self._elem,key,value)
                for attr in self._elem.attributes:
                    if attr.name == key:
                        self._attrs[key] = attr
                        return
                raise Exception("Attribute '"+key+"' cannot be set.")
            else:
                raise Exception("Attribute '"+key+"' cannot be set.")

    def __delitem__(self,key):
        del self._attrs[key]
        self._elem.elt.removeAttribute(key)

class Plugin(EventMixin):
    def __init__(self,node,element):
        self._owner = node
        self._element = element

    def bind_ctx(self,context):
        pass

class TagPlugin(Plugin):
    def __init__(self, node, element):
        super().__init__(node,element)

class AttrPlugin(Plugin):
    def __init__(self,node,element,value):
        super().__init__(node,element)

class ErrorPlugin(Plugin):
    def __init__(self,node,element,ex):
        super().__init__(node,element)
        self._ex = ex
        self._element <= html.SPAN(str(ex))

class TextPlugin(Plugin):
    def __init__(self,node,element):
        super().__init__(node,element)
        self._observer = ExpObserver(element.text,expression_type=ET_INTERPOLATED_STRING)
        self._observer.bind('change',self._change_handler)

    def bind_ctx(self,ct):
        self._observer.watch(ct)
        self._observer.evaluate()
        self._element.text = self._observer.value

    def _change_handler(self,event):
        self._element.text = event.data['new']

    def __repr__(self):
        return "TextPlugin('"+self._observer._exp_src.replace("\n","\\n")+"') = '"+self._element.text.replace("\n","\\n")+"'"

class TplNode(EventMixin):
    ATTR_PLUGINS = {}
    TAG_PLUGINS = {}
    PLUGIN_PREFIX='tpl-'

    class FencePost:
        pass

    @classmethod
    def register_plugin(cls,plugin_class):
        plugin_name = getattr(plugin_class,'NAME',None) or plugin_class.__name__
        plugin_name = plugin_name.upper().replace('_','-')
        if issubclass(plugin_class,AttrPlugin):
           cls.ATTR_PLUGINS[plugin_name] = plugin_class
        else:
            meta = {
                'cls':plugin_class,
                'attrs':list(plugin_class.__init__.__code__.co_varnames),
                'name': plugin_name
            }
            meta['attrs'].remove('self')
            cls.TAG_PLUGINS[plugin_name]=meta

    def __init__(self,dom_element,parent=None):
        self._element = dom_element
        self._context = None
        self._plugins = []
        self._tag_plugin = None
        self._attrs = None
        self._children = []
        self._parent = parent
        self._exclude_attrs = []
        logger.debug("Cloning element...")
        self._orig_clone = self._element.clone()

        if self._element.nodeName == '#text':
            logger.debug("Creating Text plugin...")
            self._tag_plugin = TextPlugin(self,self._element)
            logger.debug("Done (text plugin).")
        else:
            canonical_tag_name = None
            tag_args = []
            for a in self._element.attributes:
                logger.debug("Testing attribute",a.name,"...")
                canonical_name = a.name[len(self.PLUGIN_PREFIX):].upper()
                if canonical_name in self.ATTR_PLUGINS:
                    try:
                        logger.debug("Creating plugin...")
                        self._plugins.append(self.ATTR_PLUGINS[canonical_name](self,self._element,a.value))
                        logger.debug("Done Creating plugin...")
                    except Exception as ex:
                        logger.warn("Error loading attr plugin: '",canonical_name,"':",ex)
                        self._plugins.append(ErrorPlugin(self,self._element,ex))
                    self._exclude_attrs.append(a.name)
                if canonical_name in self.TAG_PLUGINS:
                    canonical_tag_name = canonical_name
                    tag_args.append(a.value)
            logger.debug("Computing canonical name...")
            if canonical_tag_name is None:
                canonical_tag_name = self._element.nodeName[len(self.PLUGIN_PREFIX):]
            if canonical_tag_name in self.TAG_PLUGINS:
                meta=self._tag_plugin = self.TAG_PLUGINS[canonical_tag_name]
                kwargs = {}
                for attr in meta['attrs']:
                    try:
                        logger.debug("Getting params:",attr)
                        kwargs[attr] = getattr(self._element,attr)
                    except:
                        pass
                    self._exclude_attrs.append(attr)
                try:
                    logger.debug("Creating plugin:",meta['name'])
                    self._tag_plugin = meta['cls'](self,self._element,*tag_args,**kwargs)
                    logger.debug("Done creating plugin:",meta['name'])
                except Exception as ex:
                    logger.warn("Error loading tag plugin: '",canonical_tag_name,"':",ex)
                    self._tag_plugin = ErrorPlugin(self,self._element,ex)
            logger.debug("Building attrdict")
            self._attrs = AttrDict(self._element,self._exclude_attrs)
            logger.debug("Processing children")
            for ch in self._element.children:
                self._children.append(TplNode(ch,self))
            logger.debug("Done processing children")


    def bind_ctx(self,context):
        self._context = context
        for p in self._plugins:
            p.bind_ctx(self._context)
        if self._tag_plugin:
            self._tag_plugin.bind_ctx(self._context)
        for ch in self._children:
            if isinstance(ch,TplNode):
                ch.bind_ctx(self._context)
        if self._attrs is not None:
            self._attrs.bind_ctx(self._context)

    def _remove_plugin(self,plugin_class):
        plugs = []
        for p in self._plugins:
            if not isinstance(p,plugin_class):
                plugs.append(p)
        self._plugins = plugs

    def clone(self):
        cloned_element = self._orig_clone.clone()
        return TplNode(cloned_element)

    def append(self,node):
        if node._parent is not None:
            raise Exception("Node has a parent, cannot append.")
        self._children.append(node)
        node._parent = self
        self._element <= node._element

    def create_fence(self,node):
        start = TplNode.FencePost()
        end = TplNode.FencePost()
        pos = self._children.index(node)
        self._children.insert(pos,start)
        self._children.insert(pos+2,end)
        return start,end

    def cut(self,start,end):
        s_pos = self._children.index(start)
        e_pos = self._children.index(end)
        for ch in self._children[s_pos+1:e_pos]:
            if isinstance(ch,TplNode):
                self._element.remove(ch._element)
                ch._parent = None
        del self._children[s_pos+1:e_pos]

    def insert(self,start,end,nodes):
        e_pos=self._children.index(end)
        insert_before_elt = None
        for ch in self._children[e_pos:]:
            if isinstance(ch,TplNode):
                insert_before_elt = ch._element
                break
        if insert_before_elt is None:
            self._element <= [n._element for n in nodes]
        else:
            for n in nodes:
                self._element.insertBefore(n._element,insert_before_elt)
        for n in nodes:
            self._children.insert(e_pos,n)

    def __repr__(self):
        return "TplNode(elt:"+str(self._element)+",tag:"+str(self._tag_plugin)+")"


class Style(AttrPlugin):
    def __init__(self,node,element,style):
        super().__init__(node,element)
        pass
TplNode.register_plugin(Style)


class For(TagPlugin):
    SPEC_RE = re.compile('^\s*(?P<loop_var>[^ ]*)\s*in\s*(?P<sequence_exp>.*)$',re.IGNORECASE)
    COND_RE = re.compile('\s*if\s(?P<condition>.*)$',re.IGNORECASE)

    def __init__(self,node,element,loop_spec):
        super().__init__(node,element)

        m=For.SPEC_RE.match(loop_spec)
        if m is None:
            raise Exception("Invalid loop specification: "+loop_spec)
        else:
            m = m.groupdict()
        self._var = m['loop_var']
        sequence_exp = m['sequence_exp']
        self._exp,pos = parse(sequence_exp,trailing_garbage_ok=True)
        self._exp.bind('exp_change',self._change_chandler)
        m = For.COND_RE.match(sequence_exp[pos:])
        if m:
            self._cond = parse(m['condition'])
        else:
            self._cond = None

        elt_copy = self._element.clone()
        setattr(elt_copy,TplNode.PLUGIN_PREFIX+'for',False) # Deletes the for attribute
        self._template_node = TplNode(elt_copy)
        self._parent_node = self._owner._parent

    def bind_ctx(self,ctx):
        self._before,self._after=self._owner._parent.create_fence(self._owner)
        self._ctx = ctx
        self._exp.watch(self._ctx)
        self._update()

    def _update(self):
        try:
            self._lst = self._exp.evaluate(self._ctx)
        except Exception as ex:
            logger.warn("Exception",ex,"when computing list",self._exp,"with context",self._ctx)
            self._lst = []
        self._clones=[]
        self._parent_node.cut(self._before,self._after)
        try:
            for item in self._lst:
                c=Context({self._var:item})
                try:
                    if self._cond is None or self._cond.evaluate(c):
                        clone = self._template_node.clone()
                        clone.bind_ctx(c)
                        self._clones.append(clone)
                except Exception as ex:
                    logger.warn("Exception",ex,"when evaluating condition",self._cond,"with context",c)
        except Exception() as ex:
            logger.warn("Exception",ex,"when iterating over list",self._lst)
        self._parent_node.insert(self._before,self._after,self._clones)

    def _change_chandler(self,ev):
        self._update()

TplNode.register_plugin(For)

class Include(TagPlugin):
    def __init__(self, node, element, name):
        super().__init__(node,element)
        pass
TplNode.register_plugin(Include)

class Template(TagPlugin):
    def __init__(self, node, element, name):
        super().__init__(node,element)
        pass
TplNode.register_plugin(Template)


