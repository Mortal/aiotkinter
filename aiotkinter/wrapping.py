import os
import tkinter
import functools
import threading
import traceback

from aiotkinter.loop import TkinterEventLoopPolicy


class WrappedException(Exception):
    pass


def run_in_thread(function, max_ignored=1):
    tkinter.NoDefaultRoot()

    quit_r, quit_w = os.pipe()

    ignored = 0
    keyboard_interrupt = None

    def sigint_handler(loop, cb=None):
        def quit_readable():
            os.read(quit_r, 1)
            if cb is None:
                raise KeyboardInterrupt() from keyboard_interrupt
            cb()

        loop.add_reader(quit_r, quit_readable)

    uncaught_exception = None

    def wrapper():
        try:
            function(sigint_handler)
        except Exception:
            # Use traceback.format_exc() to ensure that no tkinter
            # objects leak out of the thread due to the exception handler.
            nonlocal uncaught_exception
            uncaught_exception = traceback.format_exc()
        # Run GC collection to ensure that tkinter objects are collected in
        # this thread and not the main thread.
        try:
            import gc
            gc.collect()
        except ImportError:
            pass

    # Set daemon=True to let the interpreter kill an un-cooperative thread
    thread = threading.Thread(None, wrapper, daemon=True)
    thread.start()
    while True:
        try:
            thread.join()
            break
        except KeyboardInterrupt as exn:
            if keyboard_interrupt is not None:
                ignored += 1
                if max_ignored and ignored >= max_ignored:
                    raise
            keyboard_interrupt = exn
            os.write(quit_w, b'x')
    if uncaught_exception is not None:
        raise WrappedException(uncaught_exception)


def threaded_sigint_wrapper(fn):
    return lambda: run_in_thread(fn)


def wrapper(fn):
    @functools.wraps(fn)
    @threaded_sigint_wrapper
    def wrapped(sigint_handler):
        loop = TkinterEventLoopPolicy().new_event_loop()
        root = fn(loop)  # type: tkinter.Tk
        sigint_handler(loop, loop.stop)
        try:
            loop.run_forever()
        finally:
            try:
                root.destroy()
            except tkinter.TclError:
                # Already destroyed?
                pass

    return wrapped
