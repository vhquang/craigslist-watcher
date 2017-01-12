(ns server
  (:gen-class)
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults site-defaults]]
            [ring.middleware.json :refer [wrap-json-response wrap-json-body]]
            [ring.adapter.jetty :refer [run-jetty]]
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

(def app
  (-> (wrap-defaults app-routes site-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)))

(defn -main [& args]
  (let [port (Integer/parseInt (get (System/getenv) "APP_PORT" "8080"))]
    (run-jetty app {:port port})))
