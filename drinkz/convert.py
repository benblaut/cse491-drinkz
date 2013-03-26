"""
Converts a given amount of milliliters, liters, ounces, gallons, or any of
the possible allowed abbreviations into milliters represented by a float.
"""

def convert_to_ml(amount):
    "Take a string of form (# unit), convert the # to ml and change unit to ml"
    amount_split = amount.split()
    float_amount = float(amount_split[0])
            
    if amount_split[1] == "ml" or amount_split[1] == "milliliter" or amount_split[1] == "milliliters":
        return float_amount
    elif amount_split[1] == "l" or amount_split[1] == "liter" or amount_split[1] == "liters":
        float_amount *= 1000
        return float_amount
    elif amount_split[1] == "oz" or amount_split[1] == "ounce" or amount_split[1] == "ounces":
        float_amount *= 29.5735
        return float_amount
    elif amount_split[1] == "gallons" or amount_split[1] == "gallon" or amount_split[1] == "g":
        float_amount *= 3785.41
        return float_amount
    else:
        print "\nIncorrect unit of measurement, use ml, g, or oz."
