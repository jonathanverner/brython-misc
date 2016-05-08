import sys
sys.path.append('/app')

from browser import window, console
from app_component import AppComponent, ClickComponent
from angular.core import JSDict, component

def main():
    window.app = JSDict({
        'AppComponent':AppComponent
    })


main()