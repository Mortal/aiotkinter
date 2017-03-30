import os
import tkinter
import threading


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
        except Exception as exn:
            nonlocal uncaught_exception
            uncaught_exception = exn
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
        raise uncaught_exception


def threaded_sigint_wrapper(fn):
    return lambda: run_in_thread(fn)
