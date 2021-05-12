
class ColorMode:
    def __init__(self, index):
        super().__init__()
        self.val = index

    def __str__(self):
        return str(self.val)

class Color(ColorMode):
    def __init__(self, val):
        if isinstance(val, Color):
            val = val.val
        super().__init__(val)

    @staticmethod
    def from_rgba(r, g, b, a):
        return Color(b << 24 | g << 16 | r << 8 | a)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        r = (self.val >> 8) & 0xFF
        g = (self.val >> 16) & 0xFF
        b = (self.val >> 24) & 0xFF
        a = self.val & 0xFF
        return '#{:0>2x}{:0>2x}{:0>2x}{:0>2x}'.format(r, g, b, a)