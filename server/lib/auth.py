import bcrypt

def auth(cap):
    def decorator(f):
        def handler(self,*args,**kwargs):
            if cap in self.session.user.capabilities:
                f(self,*args,**kwargs)
            else:
                return {'Status':'Error','Message':'Forbidden'}
        return handler
    return decorator

def logged_in(f):
    def handler(self,*args,**kwargs):
        if self.session.user is not None:
            f(self,*args,**kwargs)
        else:
            return {'Status':'Error','Message':'Forbidden'}
    return handler

class AuthMixin:
    def authorized(self, object_id, action):
        return True


#class AuthEndpoint(EndpointHandler):

    #@classmethod
    #def _chacl(cls,object_id,acl):
        #pass

    #@classmethod
    #def _getacl(cls, object_id, acl):
        #pass

    #def authorized(self, object_id, action):
        #pass

    #def _login_user(self,user):
        #pass

    #def _logout(self):
        #self.session.user = None

    #@event('status')
    #def status(self):
        #if self.session.user is None:
            #return 'logged out'
        #else:
            #return 'logged in'

    #@event('available methods')
    #def avail_methods(self):
        #return 'password'

    #@event('logout')
    #def logout(self):
        #self._logout()
        #return {'Status':'OK'}
    
    #@event('login')
    #def login(self,username, password):
        #user = self._store.get('users',{'username':username})
        #if user and bcrypt.checkpw(password,user['auth']['password']['hash']):
            #self.session.user = user
            #return {'Status':'OK'}
        #else:
            #return {'Status':'Error','Message':'Invalid user or password'}

    #@event('change password')
    #@logged_in
    #def chpw(self, oldpassword, newpassword):
        #if bcrypt.checkpw(oldpassword,self.session.user['auth']['password']['hash']):
            #self.session.user['auth']['password']['hash'] = bcrypt.hashpw(newpassword,bcrypt.gensalt())
            #self._store.save('users',self.session.user)

    #@event('change acl')
    #@logged_in
    #def chacl(self,object_id,acl):
        #pass

    #@event('get acl')
    #def getacl(self, object_id):
        #pass



