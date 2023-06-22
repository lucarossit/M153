from configparser import ConfigParser

class ConfigReader():

    def __init__(self, configfile, section) -> None:
        self.configfile, self.section = configfile, section

    # def config(filename='database.ini', section='postgresql'):
    def config(self):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(self.configfile)

        # get section, default to postgresql
        db = {}
        if parser.has_section(self.section):
            params = parser.items(self.section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(self.section, self.filename))
        return db