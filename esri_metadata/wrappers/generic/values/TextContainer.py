from .. import Container


class TextContainer(Container):
    CLASS=None

    def get_children(self):
        return {'text':self.CLASS()}
