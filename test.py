import asyncio
import tkinter
import tkinter.messagebox

from aiotkinter import (
    askyesno, async_cb, wrapper,
)


async def async_loop():
    print("Thanks for calling")
    while True:
        await asyncio.sleep(1)
        print("Ping!")


@wrapper
def main(loop):
    root = tkinter.Tk()
    text = "This is Tcl/Tk version %s" % tkinter.TclVersion
    text += "\nThis should be a Ø"
    label = tkinter.Label(root, text=text)
    label.pack()
    test = tkinter.Button(
        root, text="Click me!",
        command=lambda: root.test.configure(text="[%s]" % root.test['text']))
    test.pack()
    root.test = test

    async def quit_action():
        if await askyesno('Quit?', 'Really quit?', root, loop):
            loop.stop()

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
    return root


if __name__ == '__main__':
    main()
