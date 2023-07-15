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
- [Architecture Version 01.1](https://i.imgur.com/4vmH5wN.png) - **Current version**
- [Architecture Version 02](https://i.imgur.com/aBCdf2K.png) - Upgrade plan with new Redis Queue to progress images and more schema of data (Finished - but failed when many Queue come and can not control the finish mysql and manually trigger to run again)
- [Architecture Version 03](https://i.imgur.com/VlnOSbG.png) - Upgrade CDC (Change Data Capture) from MongoDB to MySQL (Not Done Yet - Failed when sync message through mysql)

# Version 1.1
## Prepatations
```
# Prepare env file
cp .env.example .env

# Run services to support the crawling
docker-compose up -d ecommerce-crawling-mongo ecommerce-mysql
```
## Running crawling
```
docker-compose up ecommerce-crawling-app
docker-compose up ecommerce-images-worker
docker-compose up ecommerce-mysql-worker
docker-compose up ecommerce-ingredients-worker
docker-compose up ecommerce-ingredients-html-worker
```

# Version 2.0 and 3.0
## Prepatations
```
# Prepare env file
cp .env.example .env

# Run services to support the crawling
docker-compose up -d ecommerce-crawling-mongo ecommerce-images-redis ecommerce-mysql ecommerce-zookeeper ecommerce-kafka ecommerce-debezium-connect

# JDBC sink connector
cd debezium-jdbc
# Create connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/ -d @jdbc-sink-post.json

# Update connector
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/jdbc-sink/config -d @jdbc-sink-put.json

# Debezium MongoDB CDC connector
cd debezium-jdbc
# Create connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/ -d @mongodb-source-post.json
# Update connector
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://127.0.0.1:8083/connectors/ecommerce-connector/config/ -d @mongodb-source-put.json
```
## Running crawling
```
docker-compose up ecommerce-crawling-app
docker-compose up ecommerce-images-worker
docker-compose up ecommerce-mysql-worker
docker-compose up ecommerce-ingredients-worker
docker-compose up ecommerce-ingredients-html-worker
```

# Reset database to recheck 
```
db.products.updateMany(
    { is_crawl_detail: true },
    { $set: { "is_crawl_detail" : false } }
);
```

# Backup results
- [MongoDB backup - 3.92 GB](https://1drv.ms/u/s!AoOBJPU4IXLFvSspFhB55anLlNef?e=WBTsXU)
- [MySQL backup - 4.42 GB](https://1drv.ms/u/s!AoOBJPU4IXLFvUZEY0D4SD_hy7Ws?e=Y9Stbt)
- [Images - 44.5 GB](https://1drv.ms/u/s!AoOBJPU4IXLFvTYjGod1fM59vDRr?e=PM4dba)
- [Incredients - 10.9 MB](https://1drv.ms/x/s!AoOBJPU4IXLFvTeT-UaRNsuPy9Ap?e=fFlPP4)

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

**Issues when crawling**
- Resources not enough RAM or CPU to run, not stable for QUEUE
- Resolve: not send queue, log the label to know which state running

**Can not crawl faster**
- Request showing capcha page (capcha_page.txt) - status 200 can not verify in first time
- Resolve: keep crawling until get data

**Issues late deadline**
- Divide product id to everyone in team
- Công: 0->200.000 
- Kiều Nam: 200.001->400.000
- Nam Nguyen: 400.001->600.000

Dump command:
```
mongodump -d ecommerce --uri="mongodb://ecommerce:admin@localhost:27017" --gzip
```

Restore Command:
```
mongorestore -d ecommerce --uri="mongodb://ecommerce:admin@localhost:27017" --gzip ./dump
```

Import with merge mode
```
mongoimport --uri="mongodb://ecommerce:admin@localhost:27017" -c=products -d=ecommerce --mode=merge --file=${file}.json --upsertFields=id --numInsertionWorkers=4 --jsonArray
```

**File JSON too big**
- Problem: File JSON too big (4.9GB), progress killed when memory not enough
- Resolve: split json file to streaming json file

**Run Sync MySQL long**
- Run Sync MySQL long time, 2 days only 400.000 to 500.000. Because the progress convert data to string to INSERT Many to MySQL
- Resolve: 
-- Export CSV from MongoDB and import to MySQL with new tables
```
LOAD DATA INFILE "/var/lib/mysql-files/products.csv"
INTO TABLE products
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;
```
-- Change format field id with Primary key and name of another columns
```
UPDATE ecommerce.products SET category_id = '0' WHERE category_id = '';
UPDATE ecommerce.products SET day_ago_created = '0' WHERE day_ago_created = '';

ALTER TABLE `ecommerce`.`products` 
CHANGE COLUMN `id` `id` INT NOT NULL ,
ADD PRIMARY KEY (`id`),
ADD UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE;

ALTER TABLE `ecommerce`.`products` 
CHANGE COLUMN `price` `price` BIGINT NOT NULL DEFAULT 0,
CHANGE COLUMN `rating_average` `rating_average` FLOAT NOT NULL DEFAULT 0,
CHANGE COLUMN `short_url` `short_url` VARCHAR(255) NULL DEFAULT NULL,
CHANGE COLUMN `categories.id` `categories_id` TEXT NULL DEFAULT NULL,
CHANGE COLUMN `quantity_sold.value` `selling_count` TEXT NULL DEFAULT NULL,
CHANGE COLUMN `category_id` `category_id` INT NULL DEFAULT NULL,
CHANGE COLUMN `day_ago_created` `day_ago_created` INT NULL DEFAULT NULL,
CHANGE COLUMN `description` `description` LONGTEXT NULL DEFAULT NULL ;
```
-- 

**Issues not critical**
- Kafka not get the update messages to mysql
- Resolve: not yet

# Requirement Note
**Find Ingredients**
```
db.products.find({ "specifications.attributes.code": "ingredients"});
db.products.find({ $text: {$search: "\"Thành phần\""}})
```
- Note: Need to text index description field
- Export csv with query

**Top 10 selling**
```
db.products.find({"_id": 0, "id": 1, "name": 1, "selling_count": "$quantity_sold.value"}).sort("quantity_sold.value", -1).limit;
```
**Top 10 rating**
```
db.products.find({"_id": 0, "id": 1, "name": 1, "rating_average": 1}).sort("rating_average", -1).limit(10);
```

**Top 10 rating**
```
db.products.find({"_id": 0, "id": 1, "name": 1, "rating_average": 1});
```
**Top 10 lowest price**
```
db.products.find({"_id": 0, "id": 1, "name": 1, "price": 1}).sort("price", 1).limit(10);
```
**Category Products Counting**
- Using the aggregate in mongo to get report to new collection (categories_count). Then export csv and show report
```
db.products.aggregate([
    {
        $match: {
            "categories.id": {
                $gt: 0,
            },
        },
    },
    {
        $project: {
            categories: 1,
        }
    },
    {
        $group: {
            _id: "$categories.name",
            count: {
                $sum: 1,
            },
        }
    },
    {
        $sort: {
            count: -1,
        }
    },
    {
        $skip: 0
    },
    {
        $limit: 3000
    },
    { $out : "categories_count" }
]);
```
**Brand Countries Products Counting**
- Using the aggregate in mongo to get report to new collection (brand_countries_count). Then export csv and show report
```
db.products.aggregate([
    {
        $project: {
            "id": 1,
            "specifications.attributes": 1
        }
    },
    {
        $unwind: "$specifications",
    },
    {
        $unwind: "$specifications.attributes",
    },
    {
        $match: {
            "specifications.attributes.code": "brand_country",
        },
    },
    {
        $group: {
            _id: "$specifications.attributes.value",
            count: {
                $sum: 1,
            },
        }
    },
    {
        $skip: 10,
    },
    {
        $limit: 200
    },
    { $out : "brand_countries_count" }
]);
```

# Suggestions for using those data
- We can use the specifications.attribute.code to check how many products in tiki has is_warranty_applied => which categories or which brand can trust to invest
- We have the favourate_count. I think that one how many customers added to wishlist already, we can leverage that to invest
- We have review_text base on that we know how many customers has some feedbacks about that product, can add on the rating to know which is good or bad products
- We can find other_sellers and price_comparison to see best price for products to know where to cheapest or most expensive

# Improving if have time need to do
- Write Procedure MySQL to create the sale money by price and selling_count
- Finish CDC from MongoDB to MySQL by Debezium
- Change data capture - CDC data từ MongoDB sang MySQL
- Improve and restructure codebase
- Write Unit-Test