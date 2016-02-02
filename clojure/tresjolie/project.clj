(defproject tresjolie "0.2.0-SNAPSHOT"
  :description "Utilities for processing open data related to Tampere public transport"
  :url "https://github.com/jerekapyaho/tresjolie"
  :license {:name "MIT License"
            :url "http://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.6.0"] 
                 [org.clojure/data.csv "0.1.2"] 
                 [org.clojure/tools.cli "0.3.1"] 
                 [org.clojure/data.json "0.2.5"]
                 [cheshire "5.4.0"]]
  :main ^:skip-aot com.coniferproductions.tresjolie.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
