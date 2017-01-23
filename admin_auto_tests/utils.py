

def test_base_class(cls):
    class NewCls(cls):
        def __init__(self, *args, **kwargs):
            super(NewCls, self).__init__(*args, **kwargs)
            self.users = []
            self.helper = None
            # Kludge alert: We want this class to carry test cases without being run
            # by the unit test framework, so the `run' method is overridden to do
            # nothing.  But in order for sub-classes to be able to do something when
            # run is invoked, the constructor will rebind `run' from TestCase.
            if self.__class__ != NewCls:
                # Rebind `run' from the parent class.
                self.run = NewCls.run.__get__(self, self.__class__)
            else:
                self.run = lambda self, *args, **kwargs: None
    return NewCls