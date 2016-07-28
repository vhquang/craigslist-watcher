(ns server
  (:require [compojure.core :refer :all]
            [compojure.handler :as handler]
            [compojure.route :as route]
            [ring.middleware.json :refer [wrap-json-response wrap-json-body]]
            [scrapper]))

(defroutes
  app-routes
  (GET "/" [] "It works")
  (GET "/ping" [] {:status 200 :body {:d "pong"}})
  (GET "/scrape" []
       (let [name "x"]
         {:status 200
          :body {:d (scrapper/run)}}))
  (route/resources "/")
  (route/not-found "Page not found"))

;(def route-handler (handler/site app-routes))

(def app
  (-> (handler/site app-routes)
      (wrap-json-body {:keywords? true})
      wrap-json-response))