import psycopg2

class Connection(object):
    connection_ins = None

    def __new__(cls):
        if cls.connection_ins is not None:
            cls.connection_ins = super().__init__(cls)
        return cls.connection_ins

    def __init__(self):
        self.connection = psycopg2.connect(
            host="",
            password="",
            database="",
            user=""
        )
        self.connection.autocommit = True

