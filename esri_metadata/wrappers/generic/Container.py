from . import ElementWrapper


class Container(ElementWrapper):
    def __init__(self,children=None):
        self.mapping=self.get_children() if children is None else children
        for n,w in self.mapping.items():
            w.set_name(n)


    def get_children(self):
        return {}


    def __getattr__(self,name):
        """If a physical attribute doesn't exist, check in self.mapping and bind the instance."""
        w=self.mapping.get(name,None)
        if w is not None:
            w.set_name(name)
            w.bind(self)
            return w
        else:
            raise AttributeError('{} not found in {}'.format(name,self.name))


    def __delattr__(self,name):
        w=getattr(self,name)
        w.delete()
