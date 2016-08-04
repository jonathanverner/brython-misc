from lib.events import EventMixin

class Context(object,EventMixin):
    """ Class used for looking up identifiers when evaluating an expression. """
    def __init__(self, dct={}):
        self._dct = dct
        self._saved = {}

    def __getattr__(self,attr):
        if attr in self._dct:
            return self._dct[attr]
        else:
            super().__getattribute__(attr)

    def __setattr__(self,attr,val):
        if attr == '_dct' or attr == '_saved':
            super().__setattr__(attr,val)
        else:
            self._dct[attr]=val

    def _get(self, name):
        return self._dct[name]

    def _set(self,name,val):
        self._dct[name]=val

    def _save(self, name):
        """ If the identifier @name is present, saves its value on
            the saved stack """
        if name not in self._dct:
            return
        if not name in self._saved:
            self._saved[name] = []
        self._saved[name].append(self._dct[name])

    def _restore(self,name):
        """ If the identifier @name is present in the saved stack
            restores its value to the last value on the saved stack."""
        if name in self._saved:
            self._dct[name] = self._saved[name].pop()
            if len(self._saved[name]) == 0:
                del self._saved[name]
