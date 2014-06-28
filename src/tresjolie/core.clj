(ns tresjolie.core
  (:require [clojure.data.csv]
            [clojure.java.io]
            [clojure.string :as string]
            [clojure.tools.cli :refer [parse-opts]]
            [tresjolie.geodesy])
  (:gen-class))

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

(defn stops-in-range
    "For each stop, find out its distance to the current location, and whether or not it is within a given distance"
    [stops loc dist]
    (for [x stops]
        (let [s (stop-map x)]
            (if (tresjolie.geodesy/within-distance? dist loc (stop-coords s))
                (:stop-code s)))))
; Not happy with this - you'll get the stop code for those stops that are within the given distance,
; and nil for others, so you will have to filter those later anyway. What about using clojure.core/filter here?

; Approximate geographical location of Tampere Central Square (Keskustori)
(def tampere-central-square [61.508056 23.768056])

; The argument processing is modeled after https://github.com/clojure/tools.cli#example-usage

(def app-options [
                  ["-f" "--filename FILENAME" "Filename of stops file" :default "stops.txt"]
                  ["-a" "--latitude LATITUDE" "Latitude of current location in decimal degrees" :parse-fn #(Double. %) :default (first tampere-central-square)] 
                  ["-o" "--longitude LONGITUDE" "Longitude of current location in decimal degrees" :parse-fn #(Double. %) :default (last tampere-central-square)]
                  ["-d" "--distance DISTANCE" "Distance from current location in kilometers" :parse-fn #(Double. %) :default 0.5]
                  ["-h" "--help"]
                  ])

(defn usage [options-summary]
  (->> ["Process a GTFS stops.txt file and report stops within a given distance from the current location."
        ""
        "Usage: tresjolie options"
        ""
        "Options:"
        options-summary
        ""]
       (string/join \newline)))

(defn error-msg [errors]
  (str "The following errors occurred while parsing your command:\n\n"
       (string/join \newline errors)))

(defn exit [status msg]
  (println msg)
  (System/exit status))

(defn -main
    [& args]
    (let [{:keys [options arguments errors summary]} (parse-opts args app-options)]
      (cond
        (:help options) (exit 0 (usage summary))
         errors (exit 1 (error-msg errors)))
      (let [lat (:latitude options) lon (:longitude options) dist (:distance options)] 
          (println (stops-in-range (stops (:filename options)) [lat lon] dist))))) 
; Note that you'll get nils in the result of stops-in-range. Need to learn how to filter them out.
