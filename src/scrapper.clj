(ns scrapper
  (:require [net.cgrand.enlive-html :as html])
  (:require  [clojurewerkz.urly.core :as urly]))

(def ^:dynamic *cl-url* "https://losangeles.craigslist.org/search/sss?query=macbook+retina&sort=date&min_price=700&max_price=700")

(defn fetch-url [url]
  (html/html-resource (java.net.URL. url)))

(defn get-row-items []
  (html/select (fetch-url *cl-url*)
               [:.row]))

(defn get-attr-values [nodes attr-key]
  (map #(get-in % [:attrs attr-key])
       nodes))

(defn get-first-match-text [node selector]
  (html/text (first (html/select node selector))))

(defn to-absolute-url [rel-url]
  (let [u (urly/url-like *cl-url*)]
    (if (clojure.string/index-of rel-url "//")              ; is absolute linking
      (str (urly/protocol-of u) ":" rel-url)
      (str (urly/protocol-of u) "://" (urly/host-of u) rel-url))))
;
(defn transform-row-node [row]
  (hash-map :id (get-in row [:attrs :data-pid])
            :price (clojure.string/replace
                     (get-first-match-text row [:a :span.price])
                     "$" "")
            :title (get-first-match-text row [:a.hdrlnk])
            :link (to-absolute-url
                    (first (get-attr-values
                             (html/select row [:a.hdrlnk]) :href)))
            :time (first (get-attr-values (html/select row [:time]) :datetime))
            :repost_id (get-in row [:attrs :data-repost-of])))

(defn get-description [url]
  (let [page (fetch-url url)]
    (html/text (first (html/select page [:#postingbody])))))

(defn run []
  (->>
    (map transform-row-node (get-row-items))
    (map (fn [item] (->> item
                         (get item :link)
                         (get-description)
                         (assoc item :description))))

    ))