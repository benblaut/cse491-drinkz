import db

class Recipe(object):
    def __init__(self, name = '', ingredients = [()]):
        self.name = name
        self.ingredients = ingredients
