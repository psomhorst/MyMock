import mirakuru
import subprocess
import os
from distutils.spawn import find_executable
import shutil
import sys
import psutil


class MyMock(object):

    """The MyMock object creates and maintains a mock MySQL-server."""

    pid_executor = None

    def __init__(self, **kwargs):

        def get_data_dir(port):
            return '/tmp/mymock.{}.data'.format(port)

        def get_base_dir(mysql_server):
            return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(
                                   find_executable(mysql_server))), '..'))

        def get_pid_file(port):
            return '/tmp/mymock.{}.pid'.format(port)

        def get_socket(port):
            return '/tmp/mymock.{}.sock'.format(port)

        def get_log_file(port):
            return '/tmp/mymock.{}.log'.format(port)

        def get_bin_file(port):
            return '/tmp/mymock.{}.bin'.format(port)

        def get_bin_index(port):
            return '/tmp/mymock.{}.bin.index'.format(port)

        self.port = kwargs.get('port', 9218)
        self.mysql_server = kwargs.get('mysql_server', 'mysqld_safe')
        self.mysql_init = kwargs.get('mysql_init', 'mysql_install_db')
        self.mysql_admin_exec = kwargs.get('mysql_admin_exec', 'mysqladmin')

        self.data_dir = kwargs.get('data_dir', get_data_dir(self.port))
        self.base_dir = kwargs.get('base_dir', get_base_dir(self.mysql_server))
        self.pid_file = kwargs.get('pid_file', get_pid_file(self.port))
        self.socket = kwargs.get('socket', get_socket(self.port))
        self.log_file = kwargs.get('log_file', get_log_file(self.port))
        self.bin_file = kwargs.get('bin_file', get_bin_file(self.port))
        self.bin_index = kwargs.get('bin_index', get_bin_index(self.port))

        self.host = kwargs.get('host', 'localhost')
        self.timeout = kwargs.get('timeout', 60)

        self.force = kwargs.get('force', True)

    def get_sqlalchemy_path(self):
        return 'mysql://root@{}/?unix_socket={}'.format(self.host, self.socket)

    def up(self):
        """Try to start create the data directory and start the server process."""

        def create_data_directory():
            """Try to create the data directory."""
            command = ' '.join([self.mysql_init,
                                '--user={}'.format(os.getenv('USER')),
                                '--datadir={}'.format(self.data_dir),
                                '--basedir={}'.format(self.base_dir)])

            subprocess.check_output(command, shell=True)

        def create_pid_executor():
            """Create a pid executor."""
            command = ' '.join([self.mysql_server,
                                '--datadir={}'.format(self.data_dir),
                                '--pid-file={}'.format(self.pid_file),
                                '--port={}'.format(self.port),
                                '--socket={}'.format(self.socket),
                                '--log-error={}'.format(self.log_file),
                                '--log-bin={}'.format(self.bin_file),
                                '--log-bin-index={}'.format(self.bin_index)])

            pid_executor = mirakuru.PidExecutor(command,
                                                self.pid_file,
                                                timeout=self.timeout,
                                                shell=True)

            return pid_executor, command

        if self.force:
            self.down()
            running_process = self.is_running()
            if running_process:
                running_process.terminate()

        try:
            create_data_directory()

        except Exception:
            self.down()
            type, value, traceback = sys.exc_info()
            raise Exception("Could not create directory"), None, traceback

        self.pid_executor, pid_exec_command = create_pid_executor()

        try:
            self.pid_executor.start()
        except Exception:
            self.down()
            type, value, traceback = sys.exc_info()
            raise Exception("Could not run pid executor"), None, traceback

        return True

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

    def check_running(self, cmdline_arg):
        for process in psutil.process_iter():
            try:
                if cmdline_arg in process.cmdline():
                    return process
            except psutil.AccessDenied:
                pass
        return False

    def sock_running(self):
        return self.check_running('--socket={}'.format(self.socket))

    def pid_running(self):
        return self.check_running('--pid-file={}'.format(self.pid_file))

    def datadir_running(self):
        return self.check_running('--datadir={}'.format(self.data_dir))

    def is_running(self):
        for func in (self.sock_running, self.pid_running, self.datadir_running):
            result = func()
            if result:
                return result
        return False
