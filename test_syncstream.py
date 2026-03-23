import asyncio
from asgiref.sync import async_to_sync

async def ag():
    yield b'1'
    yield asyncio.sleep(0.1)
    yield b'2'

class SyncStream:
    def __init__(self, async_gen_func):
        self.agen = async_gen_func()
        # Ensure we bind to the same loop
    
    def __iter__(self):
        return self
        
    def __next__(self):
        async def _next():
            return await self.agen.__anext__()
        
        try:
            return async_to_sync(_next)()
        except StopAsyncIteration:
            raise StopIteration

s = SyncStream(ag)
for i in s:
    print(i)
