var cfg = {
    "_id": "dbrs",
    "version": 1,
    "members": [
        {
            "_id": 0,
            "host": "ecommerce-crawling-mongo:27017",
            "priority": 2
        },
        {
            "_id": 1,
            "host": "ecommerce-crawling-mongo-rs1:27017",
            "priority": 1
        },
        {
            "_id": 2,
            "host": "ecommerce-crawling-mongo-rs2:27017",
            "priority": 1
        }
    ]
};
rs.initiate(cfg, { force: true });
rs.status();

// Update
rs.reconfig(cfg, {force: true});