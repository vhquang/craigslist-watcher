## Introduction
This project scrape Craigslist base on a given query, then use an intermediate database to cache which link you would like to skip. So, on next query, it can display only new links of interest.  

## Requirements
- Redis
- Python
- Clojure

## Installation
```
pip install -r requirements.txt
```
Refer to [Leiningen](http://leiningen.org/) website for install `lein`

## Run
For scrapping your query. Run:
```
lein ring server-headless
```
Then run a web server:
```
python app.py
```
