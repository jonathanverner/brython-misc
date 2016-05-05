import sys
sys.path.append('/app')

from browser import window
from app_component import AppComponent
from angular.core import JSDict


def main():
    app = AppComponent()
    app.register()
    window.app = JSDict({
        'AppComponent':app
    })

main()