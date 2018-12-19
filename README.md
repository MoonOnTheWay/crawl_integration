# Run command
python integration.py 
`optional arguments:`
  -h, --help            show this help message and exit
  -sy START_YEAR, --START_YEAR START_YEAR
                        start year to crawl from
  -ey END_YEAR, --END_YEAR END_YEAR
                        end year to crawl from
  -sm START_MONTH, --START_MONTH START_MONTH
                        start month to crawl from
  -em END_MONTH, --END_MONTH END_MONTH
                        end month to crawl from
  -sd START_DAY, --START_DAY START_DAY
                        start day to crawl from
  -ed END_DAY, --END_DAY END_DAY
                        end day to crawl from

1. Crawl the latest blogs (or in a given date range) from the main blog websites on the web
2. Import the crawled blogs and extracted relevant papers to the database: blogs, arxivs, blogs_arxivs
