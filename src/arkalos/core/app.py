
class App:

    VERSION: str = '0.5.0'

    _basePath: str = ''
    _envFile: str = '.env'
    _configFolder: str = '/config'
    _scriptsFolder: str = '/scripts'

    def __init__(self, base_path: str):
        self._basePath = base_path
