import sys
sys.modules['browser'] = __import__('client.tests.brython.browser')
sys.modules['browser'].html = __import__('client.tests.brython.browser.html')
sys.modules['browser'].console = __import__('client.tests.brython.browser.console')