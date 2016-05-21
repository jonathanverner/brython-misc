from browser import console

class Logger:
    SEVERITY_DEBUG = 0
    SEVERITY_LOG = 1
    SEVERITY_INFO = 2
    SEVERITY_WARN=3
    SEVERITY_ERROR=4
    SEVERITY_CRITICAL=5

    global_level = 0

    def __init__(self,prefix,level=None):
        self.prefix = prefix
        self.level = None

    def debug(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_DEBUG)

    def log(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_LOG)

    def info(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_INFO)

    def warn(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_INFO)

    def error(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_ERROR)

    def critical(self,*args):
        self.do_log(*args,severity = Logger.SEVERITY_CRITICAL)

    def do_log(self,*args,severity=0):
        if (self.level is None and severity >= Logger.global_level) or ( severity >= self.level):
            self._print_log(*args)

    def _print_log(self,*args):
        console.log(self.prefix+":",*args)



