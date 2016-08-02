#from server.tests import settings
from server.lib.settings import settings


def test_settings_default():
    conf = settings('test_settings')
    conf.default({
        'workdirs':'/tmp/wd',
        'gitolite_wd':'data/gitolite-admin',
        'gitolite_url':'ssh://git@localhost:2222',
    })
    assert conf.workdirs == '/tmp/wd'
    conf.workdirs = 'cau'
    assert conf.workdirs == 'cau'
    assert conf.ahoj is None

