# Overview
- Developer: Phong Nguyen.
- Target release: 7 July, 2023.
- Epic: Crawling data websites
- Coach: Huy Do.

# Objective
Crawling all products in the websites (tiki.vn). Statitics the data and give some suggestions to using those data to increase ROI for business team if can.
- Compare the prices between branch
- Top 10 selling products
- Top country with most products in
- ...

# Goals
- Collecting products in short terms
- Statistic the data 
- Analysis data
- Suggestion to business to increase ROI

# Overall requirement 
Get all products and attribute products to MongoDB

Change Data Capture (CDC) from MongoDB to MySQL with some specific attributes
* Product name
* Short description
* Description
* URL
* Rating
* Selling Count
* Price
* Category ID

Statistics data
* How many products in each categories
* Original of products, how many products from China, compare rate between each country
* Top 10 best selling products

Get all incredient and store to csv (only product has incredients)

Download all images to local storage

Suggest idea to use those data

# Architecture
[Architecture Version 01](https://i.imgur.com/hXIqMrh.png)

# Issues when crawling data
**Missing User Agent**
- Problem: Website response 404 status
- Resolve: simulate the User Agent in settings, enable USER_AGENT
**Many Sub Categories inside**
- Problem: Sub Categories not only in the home page, many level sub categories when crawling inside
- Resolve: Crawling inside and store all include paging (e.g total, current_page, last_page). base on those can come to inside every page
**Calculation not correct**
- Problem: Total shows 20 pages but page 19 is empty already and api showing 19 also
- Resolve: Find them and not run it
```
categories = collection.find({
    '$expr': {
        '$gt': [
            { '$subtract': ['$last_page', 1]},
            '$current_page'
        ]
    }
}).limit(${limit})
```
