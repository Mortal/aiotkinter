import asyncio
import tkinter
from functools import partial


BUTTONS = {
    'abortretryignore': ('abort retry ignore'.split(), 'abort'),
    'ok': ('ok'.split(), 'ok'),
    'okcancel': ('ok cancel'.split(), 'cancel'),
    'retrycancel': ('retry cancel'.split(), 'cancel'),
    'yesno': ('yes no'.split(), 'no'),
    'yesnocancel': ('yes no cancel'.split(), 'cancel'),
}


class Dialog(tkinter.Toplevel):
    # Based on http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    def __init__(self, loop, parent, title, message, buttons):
        super().__init__(parent, {'class': 'Dialog'})
        self.wm_attributes('-type', 'dialog')
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        body = tkinter.Frame(self)
        self.initial_focus = self.body(body, message)
        body.pack(side='top', fill='both', expand=1)
        self.buttonbox(buttons)
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.wm_delete)

        # TODO we could also implement tk.tcl PlaceWindow...
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.result = asyncio.Future(loop=loop)

    def body(self, master, message, detail=None):
        bitmap = tkinter.Label(master, image='::tk::icons::question')
        bitmap.grid(row=0, column=0, sticky='nw', padx='2m', pady='2m')
        msg = tkinter.Label(master, text=message, font='TkCaptionFont',
                            anchor='nw', justify='left')
        msg.grid(row=0, column=1, sticky='news', padx='2m', pady='2m')
        master.columnconfigure(1, weight=1)
        if detail is not None:
            dtl = tkinter.Label(master, text=detail,
                                anchor='nw', justify='left')
            dtl.grid(sticky='news', padx='2m', pady=[0, '2m'])
            master.rowconfigure(1, weight=1)
        else:
            master.rowconfigure(0, weight=1)

    def buttonbox(self, button_spec):
        if isinstance(button_spec, str):
            names, self.cancel_button = BUTTONS[button_spec]
        else:
            names, self.cancel_button = button_spec
        self.ok_button = names[0]
        box = tkinter.Frame(self)
        buttons = []

        for i, name in enumerate(names):
            label = name[0].upper() + name[1:]
            default = i == 0
            kwargs = {'default': tkinter.ACTIVE if default else tkinter.NORMAL}
            buttons.append(
                tkinter.Button(box, text=label,
                               command=partial(self.command, name),
                               **kwargs))
            # buttons[-1].pack(side=tkinter.LEFT, padx=3, pady=2)
            buttons[-1].grid(row=0, column=i, padx='3m', pady='2m', sticky='ew')
            box.columnconfigure(i, uniform='buttons')

        self.bind("<Return>", self.key_return)
        self.bind("<Escape>", self.cancel)

        box.pack(side='bottom', fill='both')
        box.anchor(tkinter.CENTER)

    def wm_delete(self):
        self.set_result(None)

    def key_return(self, ev):
        self.command(self.ok_button)

    def cancel(self, ev):
        self.set_result(None)

    def set_result(self, value):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
        self.result.set_result(value)

    def command(self, name, *args):
        try:
            method = getattr(self, 'button_' + name)
        except AttributeError:
            self.set_result(name)
        else:
            method()

    def __await__(self):
        return self.result.__await__()


async def askyesno(title, message, parent, loop):
    result = await Dialog(loop, parent, title, message, 'yesno')
    return 'yes' == result
