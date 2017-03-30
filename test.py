import os
import select
import threading
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
    def cb():
        asyncio.ensure_future(coro_fn(), loop=loop)

    return cb


def run_in_thread(function):
    quit_r, quit_w = os.pipe()

    def sigint_handler(loop, cb):
        def quit_readable():
            os.read(quit_r, 1)
            cb()

        loop.add_reader(quit_r, quit_readable)

    function_exited = threading.Event()
    uncaught_exception = None

    def wrapper():
        try:
            function(sigint_handler)
        except Exception as exn:
            nonlocal uncaught_exception
            uncaught_exception = exn
        finally:
            function_exited.set()

    thread = threading.Thread(None, wrapper)
    thread.start()
    while True:
        try:
            function_exited.wait()
            break
        except KeyboardInterrupt:
            os.write(quit_w, b'x')
    thread.join()
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
        if tkinter.messagebox.askyesno('Quit?', 'Really quit?'):
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
    # root.mainloop()
    asyncio.ensure_future(async_loop(), loop=loop)
    sigint_handler(loop, really_quit)
    loop.run_forever()


if __name__ == '__main__':
    main()
