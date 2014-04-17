""" """
import logging
logging.basicConfig(level=logging.DEBUG)

from thredis import *
from thredis.model import *

sess = UnifiedSession.from_url("redis://127.0.0.1:6379/0")


r=Record('this', session=sess)

r._egress_keys('_id','_active')





_zset = ZSet('zset', 'mine', session=sess)

_zset.add(1)
sess.execute()
_zset.add(2)
sess.execute()
_zset.add(3)
sess.execute()
_zset.add(4)
sess.execute()
_zset.add(5)
sess.execute()


_zset.all()