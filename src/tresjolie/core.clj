(require 
    '[clojure.data.csv :as csv]
    '[clojure.java.io :as io])
            
(ns tresjolie.core
  (:gen-class))

; Field names for stops, to use in a map representing a stop
(def stop-fields [:stop-id :stop-code :stop-name :stop-latitude :stop-longitude])

(defn stop-map 
    "Maps field names into vector elements representing stops"
    [stop] 
    (zipmap stop-fields stop))

(defn stops 
    "Read a CSV file with stops using clojure.data.csv, and return a lazy sequence of vectors"
    [file-name] 
    (with-open [in-file (clojure.java.io/reader file-name)] 
        (doall 
            (clojure.data.csv/read-csv in-file))))

(defn -main
  "Do whatever we want to do to a lazy sequence read from a CSV file"
  [& args]
  (doseq [x (stops (first args))] (println (stop-map x))))
