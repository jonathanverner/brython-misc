from .expression import parse
from lib.events import EventMixin

class ExpObserver(EventMixin):

    def __init__(self,expression,context):
        super().__init__()
        self._exp_src = expression
        self.ast = parse(expression)
        self.ctx = context
        self.ast.bind('exp_change',self._change_chandler)
        self.ast.watch(context)
        self.evaluate()
        self._last_event_id = -1

    def _change_chandler(self,event):
        if event.data['source_id'] == self._last_event_id:
            return
        else:
            self._last_event_id = event.data['source_id']
        event_data = {
            'exp':self._exp_src,
            'observer':self,
            'source_id':event.data['source_id']
        }
        if self._have_val:
            event_data['old']=self._val
        self.evaluate()
        if self._have_val:
            event_data['new'] = self._val
        self.emit('change',event_data)

    def have_value(self):
        return self._have_val

    def value(self):
        return self._val

    def evaluate(self):
        try:
            self._val = self.ast.evaluate(self.ctx)
            self._have_val = True
        except:
            self._have_val = False



