import scripts.glyph as glyph

class deonticglyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.is_deontic = True
        self.class_number = 4