try:
    from . import env
except:
    import env

OPERATION_MODE = env.DB_MODE

""" database credentials """
# put your db credentials here
user = 'root'
password = 'Prism@123'
host = 'localhost'
port = '3306'
db_name = 'tt'
# db credentials ends here

DB_CONFIG = dict(
    user=user,
    password=password,
    host=host,
    port=port,
    db_name=db_name,
)