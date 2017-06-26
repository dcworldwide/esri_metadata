class Wrapper(object):
    def set_name(self,name):
        self.name=name

    @property
    def is_bound(self):
        return self.parentElementWrapper is not None

    def bind(self,parentElementWrapper):
        self.parentElementWrapper=parentElementWrapper
