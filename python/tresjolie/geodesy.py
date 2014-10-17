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


MIN_LAT = math.radians(-90)
MAX_LAT = math.radians(90)
MIN_LON = math.radians(-180)
MAX_LON = math.radians(180)
    
def bounding_box(lat_deg, lon_deg, distance, radius=EARTH_EQUATORIAL_RADIUS):
    """
    Computes the bounding coordinates of all points on the surface
    of a sphere that has a great circle distance to the coordinates
    by this GeoLocation instance that is less or equal to the distance argument.
        
    distance - the distance from the coordinate point on kilometers            
    radius   - the radius of the sphere in kilometers
            
    Returns a tuple with two elements. They are themselves tuples, with the
    latitude and longitude of the SW and NE corner of the bounding box.
    """
    # Compute the angular distance in radians on the great circle
    rad_dist = distance / radius
        
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
        
    min_lat = lat - rad_dist
    max_lat = lat + rad_dist
        
    if min_lat > MIN_LAT and max_lat < MAX_LAT:
        delta_lon = math.asin(math.sin(rad_dist) / math.cos(lat))
            
        min_lon = lon - delta_lon
        if min_lon < MIN_LON:
            min_lon += 2 * math.pi
                
        max_lon = lon + delta_lon
        if max_lon > MAX_LON:
            max_lon -= 2 * math.pi
    # a pole is within the distance
    else:
        min_lat = max(min_lat, MIN_LAT)
        max_lat = min(max_lat, MAX_LAT)
        min_lon = MIN_LON
        max_lon = MAX_LON
        
    return ((math.degrees(min_lat), math.degrees(min_lon)),
            (math.degrees(max_lat), math.degrees(max_lon))) 
