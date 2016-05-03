from browser import ajax, window

class Promise():
    def __init__(self):
        pass
    
    def then(self, success_handler, error_handler):
        pass
    
class HTTPException(Exception):
    def __init__(self,request):
        super(HTTPException,self).__init__()
        self.req = request
        
    
class HTTPRequest(Promise):
    METHOD_POST = 'POST'
    METHOD_GET  = 'GET'
    STATUS_NEW = 0
    STATUS_INPROGRESS = 1
    STATUS_FINISHED = 2
    STATUS_ERROR = 3
    
    def __init__(self,url,method='GET',data=None,start_immediately=True):
        self._url = url
        self._success_handler = None
        self._error_handler = None
        self._result = None
        self._req = ajax.ajax()
        self._req.bind("complete",self._complete_handler)
        self._status = HTTPRequest.STATUS_NEW
        self._data = data
        self._method = method
        if start_immediately:
            self.start()
    
    def start(self):
        if self._status == HTTPRequest.STATUS_NEW:
            self._status = HTTPRequest.STATUS_INPROGRESS
            self._req.open(self._method,self._url,True)
            self._req.set_header('content-type','application/x-www-form-urlencoded')
            if self._data is None:
                self._req.send()
            else:
                self._req.send(self._data)
    
    def _complete_handler(self,req):
        if req.status == 200 or req.status == 0:
            self._status = HTTPRequest.STATUS_FINISHED
            self._result = req
            if self._success_handler:
                self._success_handler(self._result)
        else:
            self._status = HTTPRequest.STATUS_ERROR
            self._result = HTTPException(req)
            if self._error_handler:
                self._error_handler(self._result)
    
    def then(self, success_handler, error_handler):
        self._success_handler = success_handler
        self._error_handler = error_handler
        if self._status == HTTPRequest.STATUS_FINISHED:
            self._success_handler(self._result)
        elif self._status == HTTPRequest.STATUS_ERROR:
            self._error_handler(self._result)

def process_async(generator):
    def run(val):
        try:
            async = generator.send(val)
            succ,err = process_async(generator)
            async.then(succ,err)
        except StopIteration:
            pass
    def error(ex):
        try:
            async = generator.throw(ex)
            succ,err = process_async(generator)
            async.then(succ,err)
        except StopIteration:
            pass
            
    return run,error

def run(f,*args,**kwargs):
    generator = f(*args,**kwargs)
    async = next(generator,Promise())
    succ,err = process_async(generator)
    async.then(succ,err)

def wget_urls(urls):
    results = ''
    for url in urls:
        result = yield HTTPRequest(url)
        results = results + result.text
    print(results)


# run(wget_urls,["/media/teaching/alg110006/maze/maze.py","/media/teaching/alg110006/maze/css/style.css"])