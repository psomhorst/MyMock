import mymock
import os
import stat
import socket


def is_socket(filename):
    try:
        mode = os.stat(filename).st_mode
        return stat.S_ISSOCK(mode)
    except:
        return False


class TestMyMock:

    # kill all processes with --socket=<socket>

    def test_init(self):
        my_mock = mymock.MyMock()

        assert my_mock.port == 9218

    def test_up_down(self):
        my_mock = mymock.MyMock()

        assert not my_mock.is_running()

        my_mock.up()

        assert my_mock.is_running()

        assert os.path.isdir(my_mock.data_dir)
        assert os.path.isfile(my_mock.pid_file)
        assert is_socket(my_mock.socket)

        # test connect to server
        my_mock.down()

        assert not os.path.isdir(my_mock.data_dir)
        assert not os.path.isfile(my_mock.pid_file)
        assert not is_socket(my_mock.socket)

    def test_up_previous_running(self):
        my_mock = mymock.MyMock()

        my_mock.up()
        assert my_mock.is_running()

        my_mock2 = mymock.MyMock(force=False)
        assert my_mock2.is_running()

        my_mock.down()

    def test_up_force(self):
        my_mock = mymock.MyMock()

        my_mock.up()
        process = my_mock.is_running()
        assert process
        print process.pid

        my_mock2 = mymock.MyMock()
        assert my_mock2.is_running()

        my_mock2.up()
        process = my_mock2.is_running()
        assert process
        print process.pid

        my_mock2.down()
