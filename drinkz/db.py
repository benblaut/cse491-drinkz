"""
Database functionality for drinkz information.
"""

# private singleton variables at module level
_bottle_types_db = []
_inventory_db = []

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db
    _bottle_types_db = []
    _inventory_db = []

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.append((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    # just add it to the inventory database as a tuple, for now.
    _inventory_db.append((mfg, liquor, amount))

def check_inventory(mfg, liquor):
    for (m, l, _) in _inventory_db:
        if mfg == m and liquor == l:
            return True
        
    return False

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    amounts = []
    for (m, l, amount) in _inventory_db:
        if mfg == m and liquor == l:
            amount_split = amount.split()
            float_amount = float(amount_split[0])
            
            if amount_split[1] == "ml":
                amounts.append(float_amount)
            elif amount_split[1] == "oz":
                float_amount *= 29.5735
                amounts.append(float_amount)
            else:
                print "\nIncorrect unit of measurement for \'%s %s %s\', use ml or oz." % (m, l, amount)

            total = sum(amounts)
            total_amount = str(total) + " ml"

    return total_amount

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for (m, l, _) in _inventory_db:
        yield m, l
