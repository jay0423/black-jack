from functools import wraps
import time

# def StopWatch(func) :
#     @wraps(func)
#     def wrapper(*args, **kargs) :
#         start = time.time()
#         result = func(*args,**kargs)
#         elapsed_time =  time.time() - start
#         print(f"{func.__name__}は{elapsed_time}秒かかりました")
#         return result
#     return wrapper

class StopWatch:
    def __init__(self, func):
        self._func = func
        # self.func1 = 0
    def __call__(self, *args, **kwargs):
        @wraps(self._func)
        def wrapper():
            start = time.time()
            result = self._func(*args, **kwargs)
            elapsed_time =  time.time() - start
            # self.func1 += elapsed_time
            print(f"{self._func.__name__}：{elapsed_time}秒")
            return result
        return wrapper