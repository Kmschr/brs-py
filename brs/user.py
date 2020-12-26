
class User:
    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{} ({})'.format(self.name, self.uuid)

class BrickOwner(User):
    def __init__(self, name, uuid, brickcount):
        super().__init__(name, uuid)
        self.brickcount = brickcount

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{} {:,} bricks'.format(super().__str__(), self.brickcount)