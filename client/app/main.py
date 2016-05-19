import sys

from browser import window, console
from app_component import AppComponent
from angular.core import bootstrap

def main():
    bootstrap(AppComponent)

main()