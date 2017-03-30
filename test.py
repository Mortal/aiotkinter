import asyncio
import tkinter
import tkinter.messagebox

from aiotkinter import (
    askyesno, TkinterEventLoopPolicy, async_cb,
    threaded_sigint_wrapper,
)


async def async_loop():
    print("Thanks for calling")
    while True:
        await asyncio.sleep(1)
        print("Ping!")


@threaded_sigint_wrapper
def main(sigint_handler):
    loop = TkinterEventLoopPolicy().new_event_loop()

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
        if await askyesno('Quit?', 'Really quit?', root, loop):
            really_quit()

    root.protocol("WM_DELETE_WINDOW", async_cb(quit_action, loop))
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
    main()
