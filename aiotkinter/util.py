import asyncio
import traceback


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
