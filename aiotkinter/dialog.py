import asyncio
import tkinter


class Dialog(tkinter.Toplevel):
    # Based on http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    def __init__(self, loop, parent, title, message):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        body = tkinter.Frame(self)
        self.initial_focus = self.body(body, message)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.result = asyncio.Future(loop=loop)

    def body(self, master, message: str):
        tkinter.Label(master, text=message).grid(row=0)

    def buttonbox(self):
        box = tkinter.Frame(self)

        w = tkinter.Button(box, text="OK", width=10, command=self.ok,
                           default=tkinter.ACTIVE)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)
        w = tkinter.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.close()
        self.result.set_result(True)

    def cancel(self, event=None):
        self.result.set_result(False)
        self.close()

    def close(self):
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        return True

    def apply(self):
        pass


async def askyesno(title, message, parent, loop):
    d = Dialog(loop, parent, title, message)
    return await d.result
