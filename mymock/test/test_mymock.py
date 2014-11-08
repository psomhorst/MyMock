from .. import mymock


class TestMyMock:

    def test_init(self):
        my_mock = mymock.MyMock()

        assert my_mock.port == 9218

    def test_up(self):
        my_mock = mymock.MyMock()

        my_mock.up()
