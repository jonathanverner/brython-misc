from .expression import parse, ET_EXPRESSION, ET_INTERPOLATED_STRING, parse_interpolated_str
from lib.events import EventMixin

class ExpObserver(EventMixin):

    def __init__(self,expression,context, expression_type=ET_EXPRESSION):
        super().__init__()
        self._exp_src = expression
        self._exp_type = expression_type
        if expression_type == ET_EXPRESSION:
            self.asts = [parse(expression)]
        else:
            self.asts = parse_interpolated_str(expression)
        self.ctx = context
        for ast in self.asts:
            ast.bind('exp_change',self._change_chandler)
            ast.watch(context)
        self.evaluate()
        self._last_event_id = -1

    @property
    def context(self):
        return self.ctx

    @context.setter
    def context(self,ctx):
        self.ctx.reset(ctx)

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
        if self._exp_type == ET_EXPRESSION:
            try:
                self._val = self.asts[0].evaluate(self.ctx)
                self._have_val = True
            except:
                self._have_val = False
        else:
            self._val = ""
            for ast in self.asts:
                try:
                    self._val += ast.evaluate(self.ctx)
                except:
                    pass
            self._have_val = True



