from decimal import Decimal

class RotationType:
    """Represents different rotation types."""
    RT_WHD = 0
    RT_HWD = 1
    RT_HDW = 2
    RT_DHW = 3
    RT_DWH = 4
    RT_WDH = 5

    # List of all rotation types
    ALL = [RT_WHD, RT_HWD, RT_HDW, RT_DHW, RT_DWH, RT_WDH]
    
    # Upright rotations or 'not updown'
    Notupdown = [RT_WHD, RT_HWD]


class Axis:
    """Represents the axes for width, height, and depth."""
    WIDTH = 0
    HEIGHT = 1
    DEPTH = 2

    # List of all axes
    ALL = [WIDTH, HEIGHT, DEPTH]


def rectIntersect(item1, item2, x, y):
    """
    Checks if two items intersect along a given pair of axes (x, y).
    
    Parameters:
    - item1, item2: Objects with `getDimension()` and `position` attributes.
    - x, y: Indices representing the axes to check intersection on (e.g., Axis.WIDTH, Axis.HEIGHT).

    Returns:
    - True if the two items intersect along the given axes, False otherwise.
    """
    d1 = item1.getDimension()
    d2 = item2.getDimension()

    cx1 = item1.position[x] + d1[x] / 2
    cy1 = item1.position[y] + d1[y] / 2
    cx2 = item2.position[x] + d2[x] / 2
    cy2 = item2.position[y] + d2[y] / 2

    ix = abs(cx1 - cx2)
    iy = abs(cy1 - cy2)

    return ix < (d1[x] + d2[x]) / 2 and iy < (d1[y] + d2[y]) / 2


def intersect(item1, item2):
    """
    Checks if two items intersect in all 3 dimensions: width, height, and depth.
    
    Parameters:
    - item1, item2: Objects with `getDimension()` and `position` attributes.
    
    Returns:
    - True if the items intersect in all three axes, False otherwise.
    """
    return (
        rectIntersect(item1, item2, Axis.WIDTH, Axis.HEIGHT) and
        rectIntersect(item1, item2, Axis.HEIGHT, Axis.DEPTH) and
        rectIntersect(item1, item2, Axis.WIDTH, Axis.DEPTH)
    )


def getLimitNumberOfDecimals(number_of_decimals):
    """
    Generates a Decimal object representing the limit for a given number of decimals.
    
    Parameters:
    - number_of_decimals: Number of decimal places for the limit.
    
    Returns:
    - A Decimal object representing the limit (e.g., for 2 decimals, returns 0.01).
    """
    return Decimal('1.{}'.format('0' * number_of_decimals))


def set2Decimal(value, number_of_decimals=0):
    """
    Converts a value to a Decimal with the specified number of decimal places.
    
    Parameters:
    - value: The value to convert to Decimal.
    - number_of_decimals: The number of decimal places to round to (default is 0).
    
    Returns:
    - The value as a Decimal, rounded to the specified number of decimal places.
    """
    limit = getLimitNumberOfDecimals(number_of_decimals)
    return Decimal(value).quantize(limit)
