import asyncio
import tkinter

from aiohttp import web

from aiotkinter import askyesno, threaded_sigint_wrapper, TkinterEventLoopPolicy


@threaded_sigint_wrapper
def main(sigint_handler):
    loop = TkinterEventLoopPolicy().new_event_loop()
    sigint_handler(loop)
    root = tkinter.Tk()

    def exit_soon():
        def exit():
            raise KeyboardInterrupt()

        loop.call_soon(exit)

    root.protocol('WM_DELETE_WINDOW', exit_soon)

    chat = []

    async def handle(request: web.Request):
        if request.method == 'POST':
            data = await request.post()
            if 'm' in data:
                print('From', request.transport.get_extra_info('peername'),
                      repr(data['m']))
                chat.append(data['m'])
                update_chat()
        body = '<form method=post><input name=m></form><pre>' + '\n'.join(chat)
        return web.Response(text=body, content_type='text/html')

    app = web.Application(loop=loop)
    app.router.add_get('/', handle)
    app.router.add_post('/', handle)

    chat_label = tkinter.Label(root, justify='left', anchor='nw')
    chat_entry = tkinter.Entry(root)
    chat_label.grid(row=0, column=0, sticky='news', padx='2m', pady='2m')
    chat_entry.grid(row=1, column=0, padx='2m', pady='2m')
    chat_entry.focus_set()
    root.rowconfigure(0, weight=1)

    def key_return(_ev):
        chat.append(chat_entry.get())
        chat_entry.delete(0, tkinter.END)
        update_chat()

    root.bind('<Return>', key_return)

    def update_chat():
        chat_label.configure(text='\n'.join(chat))

    try:
        web.run_app(app, loop=loop)
    finally:
        root.destroy()


if __name__ == '__main__':
    main()
