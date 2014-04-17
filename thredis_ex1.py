""" """
import logging
logging.basicConfig(level=logging.DEBUG)

from thredis import UnifiedSession
from thredis.model import *


sess = UnifiedSession.from_url("redis://127.0.0.1:6379/0")

_string = String('string', 'this', session=sess)
_string.set('foobar!')
sess.execute()
_string.get()
_string.delete()
sess.execute()
_string.get()

_set = Set('sets', 'foo', session=sess)
_set.all()

_list = List('list', 'mylist', session=sess)
_list.lpush('boobles!')
sess.execute()
_list.all()

_zset = ZSet('zset', 'mine', session=sess)
_zset.add('foobles')
_zset.all()

_hash = Hash('hash', session=sess)
_hash.set('12345', {'user':'first!'})
_hash.get('12345')