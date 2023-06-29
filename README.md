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

**Reference**
[Github](https://github.com/debezium/debezium-examples/tree/main/unwrap-mongodb-smt)

Statistics data
* How many products in each categories
* Original of products, how many products from China, compare rate between each country
* Top 10 best selling products

Get all incredient and store to csv (only product has incredients)

Download all images to local storage

Suggest idea to use those data

# Architecture
- [Architecture Version 01](https://i.imgur.com/hXIqMrh.png) - First planning
- [Architecture Version 02](https://i.imgur.com/aBCdf2K.png) - Upgrade plan with new Redis Queue to progress images and more schema of data
- [Architecture Version 03](https://i.imgur.com/OxlUmrX.png) - Upgrade CDC (Change Data Capture) from MongoDB to MySQL

# Preparations
```
# Prepare env file
cp .env.example .env

# Run services to support the crawling
docker-compose up -d ecommerce-crawling-mongo ecommerce-images-redis ecommerce-mysql ecommerce-zookeeper ecommerce-kafka ecommerce-debezium-connect

# JDBC sink connector
cd debezium-jdbc
# Create connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://${ecommerce-debezium-connect}:8083/connectors/ -d @jdbc-sink-post.json

# Update connector
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/jdbc-sink/config -d @jdbc-sink-put.json

# Debezium MongoDB CDC connector
cd debezium-jdbc
# Create connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://${ecommerce-debezium-connect}:8083/connectors/ -d @mongodb-source-post.json
# Update connector
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/ecommerce-connector/config/ -d @mongodb-source-put.json
```

# Running crawling
```
docker-compose up ecommerce-crawling-app
```

# Backup results
```

```

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
**Duplicate Data**
- Problem: Crawl sometimes will get duplicate products because of bugs or logic failed
- Resolve: Using Aggregation to find
```
// Products Collection
db.products.aggregate([
    {
        $group: {
            _id: "$id",
            count: { $sum: 1 },
        },
    },
    {
        $match: {
            _id: { $ne: null },
            count: { $gt: 1 },
        },
    },
    { 
        $sort: { 
            count: -1 
        } 
    },
    { 
        $project: { 
            id: "$_id", 
            _id: 0 
        } 
    },
]);
```
```
// Categories Collection
db.categories.aggregate([
    {
        $group: {
            _id: "$category_id",
            count: { $sum: 1 },
        },
    },
    {
        $match: {
            _id: { $ne: null },
            count: { $gt: 1 },
        },
    },
    { 
        $sort: { 
            count: -1 
        } 
    },
    { 
        $project: { 
            category_id: "$_id", 
            _id: 0 
        } 
    },
]);
```

# Suggestions for using those data