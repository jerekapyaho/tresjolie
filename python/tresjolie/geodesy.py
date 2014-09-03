import math

EARTH_EQUATORIAL_RADIUS = 6378.1370
EARTH_POLAR_RADIUS = 6356.7523

#
# Utility functions
#
 
def geocentric_radius(latitude_degrees):
    """ 
    Computes the geocentric radius of the Earth for the given latitude.
    
    See http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius.
    """    
    latitude = math.radians(latitude_degrees)
    a = EARTH_EQUATORIAL_RADIUS
    b = EARTH_POLAR_RADIUS

    t1a = a**2 * math.cos(latitude)
    t1b = b**2 * math.sin(latitude)
    t1 = t1a**2 + t1b**2
    
    t2a = a * math.cos(latitude)
    t2b = b * math.sin(latitude)
    t2 = t2a**2 + t2b**2
    
    r = math.sqrt(t1 / t2)
    return r


def haversine(lat1_deg, lon1_deg, lat2_deg, lon2_deg, earth_radius=EARTH_EQUATORIAL_RADIUS):
    """
    Computes the distance between two geographical points in kilometers.
    
    The coordinate values are degrees.
    Uses the haversine formula (see http://en.wikipedia.org/wiki/Haversine_formula).
    This implementation is derived from the JavaScript code 
    by Andrew Hedges at http://andrew.hedges.name/experiments/haversine/.
    The Earth radius defaults to the Earth's equatorial radius.
    For added accuracy, you may want pass a radius more suitable for the
    latitudes of the points you are processing.
    """    
    lat1 = math.radians(lat1_deg)
    lon1 = math.radians(lon1_deg)
    lat2 = math.radians(lat2_deg)
    lon2 = math.radians(lon2_deg)
    
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2 
    c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) ) 
    d = earth_radius * c

    return d
