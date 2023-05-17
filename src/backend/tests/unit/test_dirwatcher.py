import time
import os
import pytest

from notesntodos.dirwatcher import DirWatcher


@pytest.fixture
def test_dir():
    os.system("mkdir -p /tmp/dw_test")
    yield
    # Clean up
    os.system("rm /tmp/dw_test/ignore*")
    os.system("rmdir /tmp/dw_test")


def test_ignore_timing(test_dir):
    import copy

    global callback_ops
    global callback_count
    callback_ops = []
    callback_count = 0

    def testCallback(ops):
        global callback_ops
        global callback_count
        callback_count += 1
        callback_ops = copy.copy(ops)

    dw = DirWatcher("/tmp/dw_test", 3, testCallback)
    try:
        time.sleep(0.1)
        os.system("touch /tmp/dw_test/ignore.not")
        dw.addIgnore("ignore.2", 2)
        os.system("touch /tmp/dw_test/ignore.2")
        dw.addIgnore("ignore.5", 5)
        os.system("touch /tmp/dw_test/ignore.5")

        # Expect no callback after 2 secs, at least 3 seconds must pass
        time.sleep(2)
        assert callback_count == 0

        # Now expect the ignore.not to be reported in callback
        time.sleep(2)
        assert callback_count == 1
        assert callback_ops == [("IN_CLOSE_WRITE", "ignore.not")]

        # Now ignore.2 should be reported
        os.system("touch /tmp/dw_test/ignore.2")
        os.system("touch /tmp/dw_test/ignore.5")
        time.sleep(2)
        assert callback_count == 1
        time.sleep(2)
        assert callback_count == 2
        assert callback_ops == [("IN_CLOSE_WRITE", "ignore.2")]

        # Now ignore.2 and ignore.5 should be reported
        os.system("touch /tmp/dw_test/ignore.2")
        os.system("touch /tmp/dw_test/ignore.5")
        time.sleep(4)
        assert callback_count == 3

        assert ("IN_CLOSE_WRITE", "ignore.2") in callback_ops
        assert ("IN_CLOSE_WRITE", "ignore.5") in callback_ops

        # Check stopping works
        assert dw.isRunning()
    finally:
        dw.stop()
        dw.join()

    assert not dw.isRunning()
