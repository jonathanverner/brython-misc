import sys
from app_component import AppComponent
from lib.angular.core import bootstrap,JSDict,_js_constructor
from jsconverters import pyobj2js

from jsmodules import jsimport
jsng = jsimport('ng')

from lib.logger import Logger
logger = Logger(__name__)


class MyExceptionHandler:
    def __init__(self):
        logger.debug("Initializing exception handler")
        pass

    def call(self, *args):
        logger.debug("Calling my exception Handler")
        logger.debug("ARGLEN:",len(args))
        logger.debug("Arguments:", *args)
        logger.debug("DIR 0", dir(args[0]))
        try:
            pass
            #logger.exception(ex)
        except:
            logger.error(*args)

    def exceptionToString(self, *args):
        logger.debug("Calling my exception to string")
        return str(args)+str(kwargs)



def main():
    bootstrap(AppComponent)
    #bootstrap(AppComponent,[jsng.core.provide(jsng.core.ExceptionHandler,JSDict({"useClass":_js_constructor(MyExceptionHandler)}))])

main()