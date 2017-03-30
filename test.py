import os
import select
import threading
import traceback
import asyncio
import aiotkinter
import tkinter
import tkinter.messagebox


async def async_loop():
    print("Thanks for calling")
    while True:
        await asyncio.sleep(1)
        print("Ping!")


def async_cb(coro_fn, loop):
    async def wrapper():
        try:
            return await coro_fn()
        except Exception:
            print('Unhandled exception in %s' % coro_fn.__name__)
            traceback.print_exc()

    def cb():
        asyncio.ensure_future(wrapper(), loop=loop)

    return cb


def run_in_thread(function, max_ignored=1):
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


def sigint_wrapper(fn):
    return lambda: run_in_thread(fn)


@sigint_wrapper
def main(sigint_handler):
    loop = aiotkinter.TkinterEventLoopPolicy().new_event_loop()

    root = tkinter.Tk()
    text = "This is Tcl/Tk version %s" % tkinter.TclVersion
    text += "\nThis should be a Ø"
    label = tkinter.Label(root, text=text)
    label.pack()
    test = tkinter.Button(root, text="Click me!",
              command=lambda: root.test.configure(
                  text="[%s]" % root.test['text']))
    test.pack()
    root.test = test

    def really_quit():
        root.destroy()
        loop.stop()

    async def quit_action():
        if tkinter.messagebox.askyesno('Quit?', 'Really quit?', master=root):
            really_quit()

    root.protocol("WM_DELETE_WINDOW", quit_action)
    quit = tkinter.Button(root, text="QUIT",
                          command=async_cb(quit_action, loop))
    quit.pack()

    # The following three commands are needed so the window pops
    # up on top on Windows...
    root.iconify()
    root.update()
    root.deiconify()

    asyncio.ensure_future(async_loop(), loop=loop)
    sigint_handler(loop, really_quit)
    loop.run_forever()


if __name__ == '__main__':
    tkinter.NoDefaultRoot()
    main()
