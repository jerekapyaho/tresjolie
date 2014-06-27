(ns tresjolie.geodesy)

; Playing around with geodesy,
; based on http://www.movable-type.co.uk/scripts/latlong.html,
; Recipe 1.18 "Performing Trigonometry" in "Clojure Cookbook",
; and Wikipedia (http://en.wikipedia.org/wiki/Earth_radius#Geocentric_radius).

; Earth's approximate radius at latitude 61.50
(def earth-radius 6371.009)

(def earth-equatorial-radius 6378.1370)
(def earth-polar-radius 6356.7523)
    
; Converts all the values in point from degrees to radians.
; The mapv function (in clojure.core since Clojure 1.4) applies
; the function to all the members of a collection and returns
; a vector. The #() is a function literal with one argument.
; Thus, the return value of this function is a vector with the
; results of applying Math.toRadians to all members of `point`.
; You would call this function like so:
; (degrees->radians [61.5, 23.75, 73.2, 2.43])
(defn degrees->radians [point]
    (mapv #(Math/toRadians %) point))

(defn square [x] (* x x))

(defn term [a b] (+ (square a) (square b)))

(defn term1-a [lat] (* (square earth-equatorial-radius) (Math/cos lat)))
(defn term1-b [lat] (* (square earth-polar-radius) (Math/sin lat)))
(defn term1 [lat] (+ (square (term1-a lat)) (square (term1-b lat))))

(defn term2-a [lat] (* (earth-equatorial-radius (Math/cos lat))))
(defn term2-b [lat] (* (earth-polar-radius (Math/cos lat))))
(defn term2 [lat] (+ (square term2-a) (square term2-b)))

(defn earth-geocentric-radius 
    "Calculate the geocentric radius of Earth at the given latitude,
     in degrees."
    [lat] (Math/sqrt (/ 
        (+ (square (* (square earth-equatorial-radius) (Math/cos lat))) (square (* (square earth-polar-radius) (Math/sin lat))))
        (+ (square (* (square earth-equatorial-radius) (Math/cos lat))) (square (* (square earth-polar-radius) (Math/sin lat))))
        )))

(defn distance-between
    "Calculate the distance in km between two points on Earth. Each
     point is a pair of degrees latitude and longitude, in that order."
    ([p1 p2] (distance-between p1 p2 earth-radius))
    ([p1 p2 radius]
        (let [[lat1 long1] (degrees->radians p1) 
              [lat2 long2] (degrees->radians p2)]
            (* radius
                (Math/acos (+ (* (Math/sin lat1) (Math/sin lat2))
                              (* (Math/cos lat1)
                                 (Math/cos lat2)
                                 (Math/cos (- long1 long2)))))))))

; "Clojure Cookbook" by Luke VanderHart and Ryan Neufeld (O’Reilly).
; Copyright 2014 Cognitect, Inc., 978-1-449-36617-9.”"Clojure Cookbook"

(defn within-distance
    "Predicate for finding out if the given point is within a distance of another.
     The distance is given as a double value in kilometers."
    ([dist p1 p2] (<= (distance-between p1 p2) dist)))
