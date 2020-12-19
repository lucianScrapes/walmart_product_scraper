# Walmart Product Scraper
This is a scraping script example using selenium.

##  :book: Features
* private proxy support
* anti-captcha (2captcha)
* export to sqlite, csv, xlsx

##  :memo: Example usage

```bash
$ scrape_products.py https://www.walmart.com/browse/top-selling-items data.csv
```

```bash
$ scrape_products.py https://www.walmart.com/browse/patio-garden/patio-chairs-seating/5428_91416_4843476?povid=91416+%7C+2019-03-01+%7C+PatioChairsandSeatingFC sqldata.db proxy:port:username:password
```

## :memo: Notes
Put your 2captcha api key in the "2CAPTCHA_API.txt" file.
While using a selenium trick, the Walmart website doesn't throw captcha challenges, even when using proxies.
