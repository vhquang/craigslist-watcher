(ns scrapper
  (:require [net.cgrand.enlive-html :as html])
  (:require [clojurewerkz.urly.core :as urly])
  (:require [clojure.tools.logging :refer [info debug]]))

(def ^:dynamic *cl-url* "https://losangeles.craigslist.org/search/sss?query=*&sort=date&min_price=700&max_price=700")

(defn fetch-url [url]
  (html/html-resource (java.net.URL. url)))

(defn get-row-items
  "Grab each craigslist item, that is put inside a `li` tag with class 'result-row',
  ex:
  <li class='result-row' data-pid='5928214568' data-repost-of='5378677845'>
  "
  [url]
  (html/select (fetch-url url)
               [:.result-row]))

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

(defn transform-row-node
  "Extract interested info (price, id, repost-id...) from the posted item"
  [row]
  (hash-map :id (get-in row [:attrs :data-pid])
            :price (->
                     (get-first-match-text row [:span.result-price])
                     (clojure.string/replace "$" ""))
            :title (get-first-match-text row [:a.hdrlnk])
            :link (to-absolute-url
                    (first (get-attr-values
                             (html/select row [:a.hdrlnk]) :href)))
            :time (first (get-attr-values (html/select row [:time]) :datetime))
            :repost_id (get-in row [:attrs :data-repost-of])))

(defn get-posting-detail [url]
  (let [page (fetch-url url)]
    (html/text (first (html/select page [:#postingbody])))))

(defn future-get-detail
  "Return a future call of getting object detail"
  [url]
  (future (get-posting-detail url)))

(defn add-item-detail
  "Retrieve more description, by GET their item link"
  [item]
  (debug "ITEM" (get item :title))
  (as-> [item] x
        (get-posting-detail (item :link))
        (clojure.string/replace x "QR Code Link to This Post" "")
        (clojure.string/trim x)
        (assoc item :description x)))

(defn concurrent-add-items-detail
  "Concurrently request item detail, and add their detail into the item"
  [items]
  (->>
    items
    (map (fn [item]
           (assoc item :description (future-get-detail (item :link)))))
    (doall)
    (map (fn [item]
           (info "ITEM" (get item :title))
           (as-> [item] x
             (deref (item :description))
             (clojure.string/replace x "QR Code Link to This Post" "")
             (clojure.string/trim x)
             (assoc item :description x))))))

(defn list-to-hashmap
  "Convert [{:id 'a'}] to {:a {:id 'a'}}"
  [list]
  (zipmap (map #(keyword (get % :id)) list)
          list))

(defn run [url]
  (binding [*cl-url* url]
    (->>
      (get-row-items url)
      (map transform-row-node)
      (pmap add-item-detail)
      ;(concurrent-add-items-detail)
      (list-to-hashmap))
    ))
