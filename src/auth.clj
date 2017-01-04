(ns autthentication
  (:require [google-apps-clj.credentials :refer [get-auth-map]]))

(def g (clojure.edn/read-string (slurp "config/google-creds.edn")))

;https://developers.google.com/identity/protocols/OAuth2
;https://developers.google.com/oauthplayground/
(defn run [] (get-auth-map g ["profile"]))
