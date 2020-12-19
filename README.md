# Walmart Product Scraper
This is a scraping script example using selenium.

##  :book: Features
* private proxy
* anti-captcha (2captcha)
* export to sqllite, csv, xlsx

##  :tangerine: Example usage:

```bash
$ scrape_products.py https://www.walmart.com/browse/top-selling-items data.csv
```

```bash
$ scrape_products.py https://www.walmart.com/browse/patio-garden/patio-chairs-seating/5428_91416_4843476?povid=91416+%7C+2019-03-01+%7C+PatioChairsandSeatingFC sqldata.db proxy:port:username:password
```

Put your 2captcha api key in the "2CAPTCHA_API.txt" file.
