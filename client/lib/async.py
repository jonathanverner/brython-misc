from browser import ajax, window,console

class PromiseException(Exception):
    def __init__(self,message):
        super(PromiseException,self).__init__(message)

class Promise:
    STATUS_NEW = 0
    STATUS_INPROGRESS = 1
    STATUS_FINISHED = 2
    STATUS_ERROR = 3

    def __init__(self,start_immediately=True,throw_on_error=True):
        self.throw_on_error = throw_on_error
        self._status  = Promise.STATUS_NEW
        self._success_handler = None
        self._error_handler = None
        self._result = None
        if start_immediately:
            self.start()
    
    def then(self, success_handler, error_handler = None):
        self._success_handler = success_handler
        self._error_handler = error_handler
        if self.status == Promise.STATUS_FINISHED and self._error_handler:
            self._success_handler(self.result)
        elif self.status == Promise.STATUS_ERROR and self._error_handler:
            self._error_handler(self.result)

    def start(self):
        if self._status == Promise.STATUS_NEW:
            self._status = Promise.STATUS_INPROGRESS
            return True
        else:
            return False

    @property
    def result(self):
        if self._status == Promise.STATUS_FINISHED or self._status == Promise.STATUS_ERROR:
            return self._result
        else:
            raise PromiseException("Not finished")

    @property
    def status(self):
        return self._status

    def _finish(self,result,status=2):
        self._result = result
        self._status = status
        if self._status == Promise.STATUS_FINISHED and self._success_handler:
            console.log("Calling success handler with results:",self.result)
            self._success_handler(self.result)
        elif self._status == Promise.STATUS_ERROR and self._error_handler:
            console.log("Calling error handler with error:", self.result)
            self._error_handler(self.result)



class Return:
    def __init__(self,val):
        self.val = val
    

class HTTPException(Exception):
    def __init__(self,request):
        super(HTTPException,self).__init__()
        self.req = request
        

class HTTPRequest(Promise):
    METHOD_POST = 'POST'
    METHOD_GET  = 'GET'

    
    def __init__(self,url,method='GET',data=None,**kwargs):
        self._url = url
        self._req = ajax.ajax()
        self._req.bind("complete",self._complete_handler)
        self._data = data
        self._method = method
        super(HTTPRequest,self).__init__(**kwargs)
    
    def start(self):
        if super(HTTPRequest,self).start():
            self._req.open(self._method,self._url,True)
            self._req.set_header('content-type','application/x-www-form-urlencoded')
            if self._data is None:
                self._req.send()
            else:
                self._req.send(self._data)
            return True
        else:
            return False
    
    def _complete_handler(self,req):
        if req.status == 200 or req.status == 0:
            self._finish(req)
        else:
            self._finish(HTTPException(req),Promise.STATUS_ERROR)


def get_continuation(generator,result,throw_on_error=False):
        
    def run(val):
        try:
            async = generator.send(val)
            if isinstance(async,Return):
                result._finish(async.val)
            else:
                succ,err = get_continuation(generator,result,throw_on_error=async.throw_on_error)
                async.then(succ,err)
        except StopIteration:
            result._finish(None)
        except Exception as ex:
            result._finish(ex,status=Promise.STATUS_ERROR)
            

    def error(ex):
        try:
            if throw_on_error:
                async = generator.throw(ex)
            else:
                async = generator.send(None)
            if isinstance(async,Return):
                result._finish(async.val)
            else:
                succ,err = get_continuation(generator,result,throw_on_error=async.throw_on_error)
                async.then(succ,err)
        except StopIteration:
            result._finish(None)
        except Exception as ex:
            result._finish(ex,status=Promise.STATUS_ERROR)
            
    return run,error


def interruptible(f):

    def run(*args,**kwargs):
        generator = f(*args,**kwargs)
        async = next(generator)
        result = Promise()
        succ,err = get_continuation(generator,result)
        async.then(succ,err)
        return result

    return run


@interruptible
def wget_urls(urls):
    results = ''
    for url in urls:
        result = yield HTTPRequest(url,throw_on_error=False)
        if result:
            results = results + result.text
    yield Return(results)



# run(wget_urls,["/media/teaching/alg110006/maze/maze.py","/media/teaching/alg110006/maze/css/style.css"])