(ns tresjolie.core
  (:require [clojure.data.csv :as csv]
            [clojure.java.io :as io]
            [clojure.string :as string]
            [clojure.tools.cli :refer [parse-opts]]
            [clojure.data.json :as json]
            [tresjolie.geodesy :as geo])
  (:gen-class))

; Defines a Stop record with the customary fields
(defrecord Stop 
  [id code name lat lon])

; Reads the stops from a CSV file into Stop records
(defn stop-records
  [file-name]
  (with-open [f (io/reader file-name)]    (doall      (->> (csv/read-csv f)        (map #(apply ->Stop %))))))

; Coerces the fields of a Stop record from strings into data
(defn coerced-stop-record
  [x]
  (->Stop (Integer/parseInt (:id x)) 
          (:code x) 
          (:name x) 
          (Double/parseDouble (:lat x)) 
          (Double/parseDouble (:lon x))))

(defn coerced-stop-records
  [xs]
  (for [x xs] (coerced-stop-record x)))

; All stops, read from CSV and coerced
(defn all-stops
  [options]
  (coerced-stop-records (stop-records (:filename options))))

; Approximate geographical location of Tampere Central Square (Keskustori)
(def tampere-central-square [61.508056 23.768056])

; The argument processing is modeled after https://github.com/clojure/tools.cli#example-usage

(def app-options [
                  ["-f" "--filename FILENAME" "Filename of stops file" :default "stops.txt"]
                  ["-a" "--latitude LATITUDE" "Latitude of current location in decimal degrees" :parse-fn #(Double. %) :default (first tampere-central-square)] 
                  ["-o" "--longitude LONGITUDE" "Longitude of current location in decimal degrees" :parse-fn #(Double. %) :default (last tampere-central-square)]
                  ["-d" "--distance DISTANCE" "Distance from current location in kilometers" :parse-fn #(Double. %) :default 0.5]
                  ["-s" "--source SOURCE" "Generate source code in SOURCE, where SOURCE = json | csharp | java | objc" :default "json"] 
                  ["-h" "--help"]
                  ])

; Options and arguments for testing, can be used in the REPL
(def test-options {:filename "/Users/Jere/tmp/stops.csv" 
                   :latitude (first tampere-central-square) 
                   :longitude (last tampere-central-square)
                   :distance 1.5
                   :source "json"})
(def test-arguments ["generate" "locate"])

(defn usage [options-summary]
  (->> ["Process a GTFS stops.txt file and generate source code, or report stops within a given distance from the specified location."
        ""
        "Usage: tresjolie [options] action"
        ""
        "Options:"
        options-summary
        "Actions:"
        "  generate    Generate source code"
        "  locate      Locate nearby stops"
        ""
        ""]
       (string/join \newline)))

(defn error-msg [errors]
  (str "The following errors occurred while parsing your command:\n\n"
    (string/join \newline errors)))

(defn exit [status msg]
  (println msg)
  (System/exit status))

(defn generated-source 
  [options] 
  (json/write-str (all-stops options)))
; This function was originally named 'source', but there already is clojure.repl/source.
; Took me a while to realize what "Source not found" from REPL actually meant...

; Generates a sequence of stops within the specified distance and location
; by filtering from the stop list all stops that match `geo/within-distance?`
(defn nearby-stops 
  [options] 
  (let [lat (:latitude options) 
        lon (:longitude options) 
        dist (:distance options)]
    (filter (fn [x] (geo/within-distance? dist [lat lon] [(:lat x) (:lon x)])) (all-stops options))))

(defn -main
  [& args]
  (let [{:keys [options arguments errors summary]} (parse-opts args app-options)]
    ;(println (str "options = " options ", arguments = " arguments))
        
    ; Handle special cases that cause us to exit
    (cond
      (:help options) (exit 0 (usage summary))
      (not= (count arguments) 1) (exit 1 (usage summary))
      errors (exit 1 (error-msg errors)))
    
    ;; Execute program with options
    (case (first arguments)
      ; Output source code
      "generate" (println (generated-source options))
      
      ; Construct a JSend-compatible response of the nearby stops
      "locate" (let [response {:status "success" 
                               :message "" 
                               :data (nearby-stops options)}]
                 (println (json/write-str response)))
      
      (exit 1 (usage summary)))))
