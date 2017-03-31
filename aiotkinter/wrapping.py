import os
import tkinter
import functools
import threading
import traceback

from aiotkinter.loop import TkinterEventLoopPolicy


class WrappedException(Exception):
    pass


class SigintHandler:
    def __init__(self, function=None, *, max_ignored=1):
        self.max_ignored = max_ignored
        self._keyboard_interrupt = None
        self._quit_r, self._quit_w = os.pipe()
        self._callback = None
        self._ignored = 0
        self._uncaught_exception = None
        if function is not None:
            self.execute(function)

    def propagate_keyboard_interrupt(self, exn):
        if self._keyboard_interrupt is not None:
            # This is not the first exception; previous was ignored.
            self._ignored += 1
            if self.max_ignored and self._ignored >= self.max_ignored:
                raise
        self._keyboard_interrupt = exn
        os.write(self._quit_w, b'x')

    def _quit_readable(self):
        os.read(self._quit_r, 1)
        if self._callback is None:
            raise KeyboardInterrupt() from self._keyboard_interrupt
        self._callback()

    def register_reader(self, loop, cb=None):
        self._callback = cb
        loop.add_reader(self._quit_r, self._quit_readable)

    def run(self, function):
        try:
            function(self.register_reader)
        except Exception:
            # Use traceback.format_exc() to ensure that no tkinter
            # objects leak out of the thread due to the exception handler.
            self._uncaught_exception = traceback.format_exc()
        # Run GC collection to ensure that tkinter objects are collected in
        # this thread and not the main thread.
        try:
            import gc
            gc.collect()
        except ImportError:
            pass

    def reraise_uncaught(self):
        if self._uncaught_exception is not None:
            raise WrappedException(self._uncaught_exception)

    def create_thread(self, function):
        # Set daemon=True to let the interpreter kill an un-cooperative thread
        return threading.Thread(None, self.run, args=(function,), daemon=True)

    def execute(self, function):
        thread = self.create_thread(function)
        thread.start()
        while True:
            try:
                thread.join()
                break
            except KeyboardInterrupt as exn:
                self.propagate_keyboard_interrupt(exn)
        self.reraise_uncaught()


def run_in_thread(function, max_ignored=1):
    tkinter.NoDefaultRoot()
    handler = SigintHandler(function, max_ignored=max_ignored)


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
