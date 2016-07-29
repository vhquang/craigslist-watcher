(ns server
  (:require [compojure.core :refer :all]
            [compojure.handler :as handler]
            [compojure.route :as route]
            [ring.middleware.json :refer [wrap-json-response wrap-json-body]]
            [scrapper]))

(def test-link "https://losangeles.craigslist.org/search/sss?query=*&sort=date&min_price=700&max_price=700")

(defroutes
  app-routes
  (GET "/" [] "It works")
  (GET "/ping" [] {:status 200 :body {:d "pong"}})
  (GET "/test" [] {:status 200 :body (scrapper/run test-link)})
  (POST "/scrape" request
    (let [link (get-in request [:body :link])]
      {:status 200
      :body (scrapper/run link)}))
  (route/resources "/")
  (route/not-found "Page not found"))

;(def route-handler (handler/site app-routes))

(def app
  (-> (handler/site app-routes)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)))