# MyBusStand Django Project

# Python 3.14 compatibility patch for Django's BaseContext.__copy__
# In Python 3.14, copy(super()) fails with:
# AttributeError: 'super' object has no attribute 'dicts' and no __dict__ for setting new attributes
try:
    import django.template.context as _context

    def _basecontext_copy(self):
        cls = self.__class__
        duplicate = cls.__new__(cls)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _context.BaseContext.__copy__ = _basecontext_copy
except Exception:
    pass
