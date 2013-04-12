"""
Module to load in bulk data from text files.
"""

# ^^ the above is a module-level docstring.  Try:
#
#   import drinkz.load_bulk_data
#   help(drinkz.load_bulk_data)
#

import csv                              # Python csv package

import recipes
import db                        # import from local package

def load_bottle_types(fp):
    """
    Loads in data of the form manufacturer/liquor name/type from a CSV file.

    Takes a file pointer.

    Adds data to database.

    Returns number of bottle types loaded
    """
    new_reader = data_reader(fp)
    
    n = 0
    for line in new_reader:       
        try:
            (mfg, name, typ) = line
            db.add_bottle_type(mfg, name, typ)
            n += 1
        except ValueError:
            continue
       
    set(db._bottle_types_db)

    return n

def load_inventory(fp):
    """
    Loads in data of the form manufacturer/liquor name/amount from a CSV file.

    Takes a file pointer.

    Adds data to database.

    Returns number of records loaded.

    Note that a LiquorMissing exception is raised if bottle_types_db does
    not contain the manufacturer and liquor name already.
    """
    new_reader = data_reader(fp)

    n = 0
    for (mfg, name, amount) in new_reader:
        n += 1
        db.add_to_inventory(mfg, name, amount)

    return n
    
def load_recipes(fp):
    """
    Loads in data of the form manufacturer/liquor name/amount from a CSV file.

    Takes a file pointer.

    Adds data to database.

    Returns number of recipes loaded.
    """
    new_reader = data_reader(fp)
    
    x = []
    n = 0
    for curr_rec in new_reader:
        try:
            ingredients = []
            for i in range(1, len(curr_rec), 2):
                try:
                    ingredients.append((curr_rec[i], curr_rec[i+1]))
                except IndexError:
                    print "Check formatting"
            r = recipes.Recipe(curr_rec[0], ingredients)
            db.add_recipe(r)
        except ValueError:
            print "Check usage"
        else:
            n += 1
    return n
    
def data_reader(fp):
    reader = csv.reader(fp)

    x = []
    for line in reader:
       if line:
         if line[0].startswith('#'):
           continue
       if not any(field.strip() for field in line):
         continue
       
       x.append(line)
       
    return x
