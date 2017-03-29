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


def main():
    asyncio.set_event_loop_policy(aiotkinter.TkinterEventLoopPolicy())
    loop = asyncio.get_event_loop()  # type: asyncio.BaseEventLoop
    quitted = asyncio.Event(loop=loop)

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

    async def quit_action():
        if tkinter.messagebox.askyesno('Quit?', 'Really quit?'):
            root.destroy()
            quitted.set()

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
    loop.run_until_complete(quitted.wait())


if __name__ == '__main__':
    main()
