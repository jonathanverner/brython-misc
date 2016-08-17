from lib.events import EventMixin
from browser import html
from .expobserver import ExpObserver
from .expression import ET_INTERPOLATED_STRING, parse
from .context import Context

from lib.logger import Logger
logger = Logger(__name__)

import re

class InterpolatedAttr(object):
    def __init__(self,attr,context=None):
        if context is None:
            context=Context()
        self._observer = ExpObserver(attr.value,context,expression_type=ET_INTERPOLATED_STRING)
        self._observer.bind('change',self._change_handler)
        self._attr=attr
        self._attr.value=self._observer.value()

    @property
    def context(self):
        return self._observer.context

    @context.setter
    def context(self,ct):
        self._observer.context = ct

    @property
    def src(self):
        return self._observer._exp_src

    @property
    def value(self):
        return self._attr.value

    @value.setter
    def value(self,value):
        self._observer.unbind()
        self._observer = ExpObserver(value,self.context,expression_type=ET_INTERPOLATED_STRING)
        self._observer.bind('change',self._change_handler)
        self._attr.value = self._observer.value()

    def _change_handler(self,event):
        self._attr.value = event.data['new']

class AttrDict(object):
    def __init__(self,element,exclude=[]):
        self._attrs = {}
        self._ctx = Context()
        self._elem = element
        self._exclude = exclude
        for a in self._elem.attributes:
            if not a.name in exclude:
                self._attrs[a.name] = InterpolatedAttr(a,self._ctx)
            else:
                self._attrs[a.name] = a

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx = ct
        for (a,interp_attr) in self._attrs.items():
            if isinstance(interp_attr,InterpolatedAttr):
                interp_attr.context = ct

    def bind_ctx(self,ct):
        self.context = ct

    def __iter__(self):
        return iter(self._attrs)

    def keys(self):
        return self._attrs.keys()

    def items(self):
        return self._attrs.items()

    def __getitem__(self, key):
        return self._attrs[key].value

    def __setitem__(self, key, value):
        if key in self._attrs:
            self._attrs[key].value = value
        else:
            if key not in self._exclude:
                setattr(self._elem,key,value)
                for attr in self._elem.attributes:
                    if attr.name == key:
                        self._attrs[key] = InterpolatedAttr(attr,self._ctx)
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
        self._observer = ExpObserver(element.text,Context(),expression_type=ET_INTERPOLATED_STRING)
        self._observer.bind('change',self._change_handler)

    def bind_ctx(self,ct):
        self._observer.context = ct

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

        if self._element.nodeName == '#text':
            self._tag_plugin = TextPlugin(self,self._element)
        else:
            canonical_tag_name = None
            tag_args = []
            for a in self._element.attributes:
                canonical_name = a.name[len(self.PLUGIN_PREFIX):].upper()
                if canonical_name in self.ATTR_PLUGINS:
                    try:
                        self._plugins.append(self.ATTR_PLUGINS[canonical_name](self,self._element,a.value))
                    except Exception as ex:
                        logger.warn("Error loading attr plugin: '",canonical_name,"':",ex)
                        self._plugins.append(ErrorPlugin(self,self._element,ex))
                    self._exclude_attrs.append(a.name)
                if canonical_name in self.TAG_PLUGINS:
                    canonical_tag_name = canonical_name
                    tag_args.append(a.value)
            if canonical_tag_name is None:
                canonical_tag_name = self._element.nodeName[len(self.PLUGIN_PREFIX):]
            if canonical_tag_name in self.TAG_PLUGINS:
                meta=self._tag_plugin = self.TAG_PLUGINS[canonical_tag_name]
                kwargs = {}
                for attr in meta['attrs']:
                    try:
                        kwargs[attr] = getattr(self._element,attr)
                    except:
                        pass
                    self._exclude_attrs.append(attr)
                try:
                    self._tag_plugin = meta['cls'](self,self._element,*tag_args,**kwargs)
                except Exception as ex:
                    logger.warn("Error loading tag plugin: '",canonical_tag_name,"':",ex)
                    self._tag_plugin = ErrorPlugin(self,self._element,ex)
            self._attrs = AttrDict(self._element,self._exclude_attrs)
            for ch in self._element.children:
                self._children.append(TplNode(ch,self))


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
            self._attrs.context=self._context

    def _remove_plugin(self,plugin_class):
        plugs = []
        for p in self._plugins:
            if not isinstance(p,plugin_class):
                plugs.append(p)
        self._plugins = plugs

    def clone(self):
        cloned_element = self._element.clone()
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
    SPEC_RE = re.compile('^\s*for\s*(?P<loop_var>[^ ]*)\s*in\s*(?P<sequence_exp>.*)$',re.IGNORECASE)
    COND_RE = re.compile('\s*if\s(?P<condition>.*)$',re.IGNORECASE)

    def __init__(self,node,element,loop_spec):
        super().__init__(node,element)

        m=For.SPEC_RE.match(loop_spec).groupdict()
        self._var = m['loop_var']
        self._exp,pos = parse(m['sequence_exp'],trailing_garbage_ok=True)
        self._exp.bind('exp_change',self._change_chandler)
        m = For.COND_RE.match(loop_spec[pos:])
        if m:
            self._cond = parse(m['condition'])
        else:
            self._cond = None

        elt_copy = self._element.clone()
        setattr(elt_copy,TplNode.PLUGIN_PREFIX+'for',False) # Deletes the for attribute
        self._template_node = TplNode(elt_copy)
        self._parent_node = self._owner._parent
        self._before,self._after=self._owner._parent.create_fence(self._owner)

    def bind_ctx(self,ctx):
        self._ctx = ctx
        self._exp.watch(self._ctx)
        self._update()

    def _update(self):
        self._lst = self._exp.evaluate(self._ctx)
        self._clones=[]
        self._parent_node.cut(self._before,self._after)
        for item in self._lst:
            c=Context({self._var:item})
            if self._cond is None or self._cond.evaluate(c):
                clone = self._template_node.clone()
                clone.bind_ctx(c)
                self._clones.append(clone)
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


