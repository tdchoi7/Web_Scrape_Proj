
# Web Scraping Project using Scrapy and Selenium
... to extract review and rating information from Tripadvisor for NYC Data Science Academy Sep 2020 Part-Time Bootcamp
- Special thanks to the instructors, mentors, TAs, and... StackOverflow!

Scrapy was run on 12/12/2020 for the top 5 attractions for Boston, Chicago, Los Angeles, and New York City
- There was a slight issue when reading NY
- This most likely was due to my computer's capacity, so the 9/11 memorial and Central Park reviews were scraped separately and added back into the data using Pandas
- In an effort to circumnavigate this issue, I have also supplied a code that runs 1 window of Chrome (rather than the multiple windows that are available on the final code) in the QuickerCode branch

Data includes City, Attraction, Review Posted Date, Attraction Visit Date, Helpful Votes for review and user, Rating, Review Text, Review Title, Username, and User Location

The analysis covers ratings, counts of 2 and 3 word combinations extracted from text, and review sentiment based on factors such as location, visit date, and helpful votes
