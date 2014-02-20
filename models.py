class Word(object):
    def __init__(self, text, left, top, right, bottom):
        self.txt = text
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

#lol-inheritance
class Column(object):
    def __init__(self, title, left, top, right, bottom):
        self.title = title
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

    def contains(self, word):
        return self.r >= word.l and word.r >= self.l
