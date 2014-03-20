""" """

if __name__ == '__main__':
    import thredis
    import time

    redis = thredis.UnifiedSession.from_url('redis://127.0.0.1:6379')

    model = Collection(redis, 'poop')

    t1 = time.time()
    id_ = model.add({'foo': True,
                        'bar': 'maybe'})

    redis.execute()

    # print(id_)
    print(model.get(id_))
    print(time.time() - t1)