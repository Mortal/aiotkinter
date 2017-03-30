import tkinter

from aiohttp import web

from aiotkinter import askyesno, threaded_sigint_wrapper, TkinterEventLoopPolicy


@threaded_sigint_wrapper
def main(sigint_handler):
    loop = TkinterEventLoopPolicy().new_event_loop()
    sigint_handler(loop)
    root = tkinter.Tk()

    async def handle(request):
        name = await askyesno('Yes or No?', 'Yes or No?', root, loop)
        text = "Hello, " + str(name)
        return web.Response(text=text)

    app = web.Application(loop=loop)
    app.router.add_get('/', handle)
    app.router.add_get('/{name}', handle)

    try:
        web.run_app(app, loop=loop)
    finally:
        root.destroy()


if __name__ == '__main__':
    main()
