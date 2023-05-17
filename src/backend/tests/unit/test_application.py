import multiprocessing
import sys
import time

from bottle import Bottle

from notesntodos.server import CustomUnicornApp


def test_custom_unicorn_app():
    def subprocess(pipe):
        from contextlib import redirect_stdout, redirect_stderr
        import io
        import signal
        import asyncio

        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(
            io.StringIO()
        ) as stderr:
            try:

                def create():
                    my_app = Bottle()
                    my_app.specialValue = 123
                    pipe.send("create_called")
                    return my_app

                def exit(my_app):
                    assert my_app.specialValue == 123
                    pipe.send("exit_called")

                CustomUnicornApp(create, exit, "127.0.0.1:8765").run()
            finally:
                pipe.send(stdout.getvalue())
                pipe.send(stderr.getvalue())
                pipe.close()

    messages = []
    try:
        dst, src = multiprocessing.Pipe(False)
        process = multiprocessing.Process(target=subprocess, args=(src,))
        process.start()
        time.sleep(1)

        # Pipe with terminate should be ok (on unix-like) because terminate uses SIGTERM and gunicorn handles it
        process.terminate()
        ret = dst.poll(1)

        assert ret
        if ret:
            # Cryptic way to get messages
            prev = None
            out = None
            err = None
            last = None
            while True:
                if prev is not None:
                    messages.append(prev)
                prev, out, err = out, err, last
                if not dst.poll(1):
                    break
                last = dst.recv()

            if out:
                sys.stdout.write(out)
            if err:
                sys.stderr.write(err)

        process.join()
    finally:
        dst.close()

    assert "create_called" == messages[0]
    assert "exit_called" == messages[1]
    assert process.exitcode == 0
