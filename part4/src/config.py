import yaml


class YamlConfig(object):
    def __init__(self, file):
        self.file = file

    def read_yaml(self, encoding='utf-8'):
        with open(self.file, encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    def write_yaml(self, wtdata, encoding='utf-8'):
        with open(self.file, encoding=encoding, mode='w') as f:
            yaml.dump(wtdata, stream=f, allow_unicode=True)


if __name__ == '__main__':
    ya = YamlConfig('config.yaml')
    data = ya.read_yaml()
    print(data)
    # ya.write_yaml(data)
