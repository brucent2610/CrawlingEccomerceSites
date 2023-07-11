{_id: 0, id: 1, name: 1, short_description: 1, description: 1, url_key: 1, rating_average: 1, "category_id": "$categories.id", price: 1, "selling_count": "$quantity_sold.value"}
{_id: 0, id: 1, name: 1, short_description: 1, description: 1, url_key: 1, rating_average: 1, "category_id": "$categories.id", price: 1, "selling_count": "$quantity_sold.value"}

ALTER TABLE `ecommerce`.`products3` 
CHANGE COLUMN `price` `price` INT NULL DEFAULT 0 ,
CHANGE COLUMN `rating_average` `rating_average` FLOAT NULL DEFAULT 0 ,
CHANGE COLUMN `category_id` `category_id` INT NULL DEFAULT 0 ,
CHANGE COLUMN `selling_count` `selling_count` INT NULL DEFAULT 0 ;

SELECT * FROM ecommerce.products3;

SET SQL_SAFE_UPDATES = 0;
UPDATE ecommerce.products3 SET category_id = json_extract(categories, '$.id') WHERE categories IS NOT NULL;
UPDATE ecommerce.products3 SET selling_count = json_extract(quantity_sold, '$.value') WHERE quantity_sold IS NOT NULL;
SET SQL_SAFE_UPDATES = 1;


SHOW GLOBAL VARIABLES LIKE 'local_infile';

SET GLOBAL local_infile=1;
LOAD DATA LOCAL INFILE '/var/lib/mysql-files/products.csv' INTO TABLE products_import
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(@col1,@col2,@col3,@col4,@col5,@col6,@col7,@col8,@col9) set category_id=@col2,day_ago_created=@col3,description=@col4,product_id=@col5,name=@col6,price=@col7,selling_count=@col8,rating=@col9;
SET GLOBAL local_infile=0;

NOTE: Try and messy data, not good to use