-- Geodesy functions modelled after http://www.movable-type.co.uk/scripts/latlong.html
module Geodesy
( GeoPt(..)
, distanceBetween
, withinDistance
, geocentricRadius
) where

-- A geographical point with latitude and longitude.
-- Using the record syntax to get named lookup.
-- Instances of GeoPts can be compared, so we derive Eq.
-- Also derive Show for printing out.
data GeoPt = GeoPt { latitude :: Double
                   , longitude :: Double
                   } deriving (Eq, Show)

-- Earth's approximate radius at latitude 61.50
earthRadius = 6357.959706678803

earthEquatorialRadius = 6378.1370
earthPolarRadius = 6356.7523


square :: Double -> Double
square x = x * x

deg2rad :: Double -> Double
deg2rad x = 2.0 * pi * x / 360.0

geocentricRadius :: Double -> Double
geocentricRadius lat = let t1a = square ((square earthEquatorialRadius) * (cos lat))
                           t1b = square ((square earthPolarRadius) * (sin lat))
                           t2a = square (earthEquatorialRadius * (cos lat))
                           t2b = square (earthPolarRadius * (sin lat))
                           t1 = t1a + t1b
                           t2 = t2a + t2b
                       in sqrt (t1 / t2)

-- Returns the distance in kilometers between two geographical points
distanceBetween :: GeoPt -> GeoPt -> Double -> Double
distanceBetween p1 p2 radius = let lat1 = deg2rad (latitude p1)
                                   lon1 = deg2rad (longitude p1)
                                   lat2 = deg2rad (latitude p2)
                                   lon2 = deg2rad (longitude p2)
                                   dt = lat2 - lat1
                                   dl = lon2 - lon1
                                   a = square (sin (dt / 2)) + cos lat1 * cos lat2 * square (sin (dl / 2))
                                   c = 2.0 * (atan2 (sqrt a) (sqrt (1 - a)))
                               in radius * c

-- Returns True or False depending on whether the given point is within some distance
-- of another point. The distance is given as a double value in kilometers.
withinDistance :: Double -> GeoPt -> GeoPt -> Double -> Bool
withinDistance dist p1 p2 radius = distanceBetween p1 p2 radius <= dist

