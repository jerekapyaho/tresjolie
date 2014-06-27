(ns tresjolie.core
  (:gen-class))

(require 
    'clojure.data.csv
    'clojure.java.io
    'tresjolie.geodesy)

; Field names for a stop, to be used as keys in a map representing a stop
(def stop-fields [:stop-id :stop-code :stop-name :stop-latitude :stop-longitude])

(defn stop-map 
    "Maps field names into vector elements representing stops"
    [x] 
    (zipmap stop-fields x))

(defn stop-coords
    "Returns the coordinates of a stop as a latitude longitude pair in a vector, converted to doubles"
    [x]
    (let [lat (Double/parseDouble (:stop-latitude x)) lon (Double/parseDouble (:stop-longitude x))]
        [lat lon]))

(defn stops 
    "Reads a CSV file with stops using clojure.data.csv, and returns a lazy sequence of vectors"
    [file-name] 
    (with-open [in-file (clojure.java.io/reader file-name)] 
        (doall 
            (clojure.data.csv/read-csv in-file))))

(def here [61.5 23.75])

(defn -main
    "For each stop defined in the CSV file, find out its distance to here, and whether it is within 0.5 km of here"
    [& args]
    (println (for [x (stops (first args))]
        (let [s (stop-map x)]
            [(:stop-code s)
             (tresjolie.geodesy/distance-between here (stop-coords s))
             (tresjolie.geodesy/within-distance 0.5 here (stop-coords s))]))))
