import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from django.http import StreamingHttpResponse

async def agen():
    yield b'A'
    yield b'B'

r = StreamingHttpResponse(agen())
try:
    # Under WSGI, Django converts the iterator
    it = iter(r)
    print('N1:', next(it))
    print('N2:', next(it))
except Exception as e:
    print('Error:', e)
