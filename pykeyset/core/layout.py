class Layout:
    def __init__(self):
        raise NotImplementedError

    @classmethod
    def layout(cls, ctx):
        """generate a layout diagram from the loaded resources"""

        raise NotImplementedError

    def drawlegend(self, ctx, key, g):
        raise NotImplementedError

    def drawlegendrect(self, rect):
        raise NotImplementedError

    def parselegend(self, legend):
        raise NotImplementedError
