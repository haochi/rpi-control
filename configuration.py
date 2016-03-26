import json

class Configuration(object):
    def __init__(self):
        self.config = None

    def get(self, key, default=None):
        if key in self.config:
            return self.config[key]
        return default

    @staticmethod
    def load(configuration_file):
        with open(configuration_file) as config_file:
            config_json = json.load(config_file)
            configuration = Configuration()
            configuration.config = config_json
            return configuration
