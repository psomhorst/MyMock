import subprocess
import mirakuru
import os
from distutils.spawn import find_executable
import shutil


class MyMock(object):

    pid_executor = None

    def __init__(self, **kwargs):

        def get_data_dir(port):
            return '/tmp/mymock.{}.data'.format(port)

        def get_base_dir(mysql_server):
            print find_executable(mysql_server)
            print os.path.realpath(find_executable(mysql_server))
            print os.path.dirname(os.path.realpath(find_executable(mysql_server)))
            print os.path.join(os.path.dirname(os.path.realpath(find_executable(mysql_server))), '..')
            print os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(find_executable(mysql_server))), '..'))
            return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(
                                   find_executable(mysql_server))), '..'))

        def get_pid_file(port):
            return '/tmp/mymock.{}.pid'.format(port)

        def get_socket(port):
            return '/tmp/mymock.{}.sock'.format(port)

        def get_log_file(port):
            return '/tmp/mymock.{}.log'.format(port)

        self.port = kwargs.get('port', 9218)
        self.mysql_server = kwargs.get('mysql_server', 'mysqld_safe')
        self.mysql_init = kwargs.get('mysql_init', 'mysql_install_db')
        self.mysql_admin_exec = kwargs.get('mysql_admin_exec', 'mysqladmin')

        self.data_dir = kwargs.get('data_dir', get_data_dir(self.port))
        self.base_dir = kwargs.get(get_base_dir(self.mysql_server))
        self.pid_file = kwargs.get('pid_file', get_pid_file(self.port))
        self.socket = kwargs.get('socket', get_socket(self.port))
        self.log_file = kwargs.get('log_file', get_log_file(self.port))

        self.host = kwargs.get('host', 'localhost')
        self.timeout = kwargs.get('timeout', 60)

    def up(self):
        command_directory = ' '.join([self.mysql_init,
                                      '--user={}'.format(os.getenv('USER')),
                                      '--datadir={}'.format(self.data_dir),
                                      '--basedir={}'.format(self.base_dir)])

        try:
            subprocess.check_output(command_directory, shell=True)
            print("MySQL mock datadir is created")
        except Exception:
            self.down()
            raise Exception("Could not create data directory ('{}')".format(command_directory))

        command_pid_executor = ' '.join([self.mysql_server,
                                         '--datadir={}'.format(self.data_dir),
                                         '--pid-file={}'.format(self.pid_file),
                                         '--port={}'.format(self.port),
                                         '--socket={}'.format(self.socket),
                                         '--log-error={}'.format(self.log_file)])

        self.pid_executor = mirakuru.PidExecutor(command_pid_executor,
                                                 self.pid_file,
                                                 timeout=self.timeout,
                                                 shell=True)

        try:
            self.pid_executor.start()
            print "MySQL server started"
        except Exception:
            self.down()
            raise Exception("Could not start server ('{}')".format(command_pid_executor))

    def down(self):
        command_shutdown = ' '.join([self.mysql_admin_exec,
                                     '--socket={}'.format(self.socket),
                                     '--user=root',
                                     'shutdown'])

        try:
            subprocess.check_output(command_shutdown, shell=True)
            print "MySQL mock server stopped."
        except Exception:
            print("Could not stop MySQL server ('{}')".format(command_shutdown))

        try:
            if os.path.isdir(self.data_dir):
                shutil.rmtree(self.data_dir)
            print("MySQL mock data directory removed.")
        except Exception:
            print("Could not remove data directory ('')".format(self.data_dir))

        try:
            self.pid_executor.stop()
        except Exception:
            print("Could not stop PID executor ().".format(self.pid_executor))

        print("MySQL mock server down.")
