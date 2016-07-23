## Introduction
This project scrape Craigslist base on a given query, then use an intermediate database to cache which link you would like to skip. So, on next query, it can display only new links of interest.  

## Requirements
- Redis
- PhantomJS
- Python

## Installation
```
pip install -r requirements.txt
```


## Run
For scrapping your query. Run:
```
python pricewatch.py
```
Then run a web server:
```
python app.py
```
