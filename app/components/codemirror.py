from angular import core as ngcore
from browser import console, timer
from jsmodules import jsimport
import javascript

CodeMirror = jsimport('CodeMirror')
CodeMirror.js_func = CodeMirror
CM = javascript.JSConstructor(CodeMirror)


class Doc:
    @ngcore.export2js
    def __init__(self,val=''):
        self._val=val
        self.change = ngcore.Output()

    def on_change(self,change):
        self._val = change.value

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self,val):
        self._val = val
        self.change.emit(val)


@ngcore.component
class CodeMirrorComponent(ngcore.Component):

    class ComponentData:
        selector = 'codemirror'
        template = '<div #textarea></div>'

        class Outputs:
            change = ngcore.Output()

        class Inputs:
            doc = Doc()
            options = ngcore.JSDict({
                'mode':ngcore.JSDict({
                    'name':'python',
                    'version':3
                }),
                'indentUnit':4
            })

        class ViewElements:
            textarea = ngcore.ViewChild('textarea')

    def __init__(self):
        super(CodeMirrorComponent,self).__init__()

    def ngAfterViewInit(self):
        self.options.value = self.doc.value
        self.cm = CM(self.textarea.nativeElement,self.options)
        self._cmdoc = self.cm.getDoc()
        self._cmdoc.on("change",self._cm_change_handler)
        self.doc.change.sub(self._doc_change_handler)

    def subscribe(self):
        pass

    def _doc_change_handler(self,change):
        self._cmdoc.setValue(self.doc.value)
        
    def _cm_change_handler(self,cmdoc,change):
        console.log(change)
        ch = ngcore.JSDict({
            'value':self._cmdoc.getValue(),
            'edit':change
        })
        console.log(self.change)
        self.change.pub(ch)
        self.doc.on_change(ch)

