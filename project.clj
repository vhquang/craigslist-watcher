(defproject watcher "0.1.1"
  :description "Parse the result page from Craigslist"
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [org.clojure/tools.logging "0.3.1"]
                 [enlive "1.1.1"]
                 [clojurewerkz/urly "1.0.0"]
                 [compojure "1.5.2"]
                 [ring/ring-json "0.4.0"]
                 [ring/ring-defaults "0.2.1"]
                 [ring/ring-jetty-adapter "1.5.1"]]
  ; plugin to support development, run "lein ring server-headless". Quick tutorial
  ; https://github.com/magomimmo/modern-cljs/blob/master/doc/first-edition/tutorial-03.md
  :plugins [[lein-ring "0.9.7"]]
  ; a handler to point to {your_namespace}/{your_handler_function}
  :ring {:handler server/app}
  :main server
  :aot [server])
