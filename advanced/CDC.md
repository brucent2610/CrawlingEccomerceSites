# Using Debezium
1. Set up MongoDB replication: Configure MongoDB to use replica sets, consisting of a primary server and one or more secondary servers (replica set members). Replication enables data changes to be propagated to the secondary servers.

2. Set up Debezium Connector with MongoDb Connection with secondary server and MySQL sink

3. Set up Kafka to get the message broker to product and consumer message

**Issues**
- Kafka can produce and consumer message but can not progress it to MySQL
- But the simple collection schema with _id and name can sync to MySQL
- Why?

# No use Debezium or Estuary

1. Set up MongoDB replication: Configure MongoDB to use replica sets, consisting of a primary server and one or more secondary servers (replica set members). Replication enables data changes to be propagated to the secondary servers.

2. Enable the oplog: The oplog (operation log) is a special capped collection in MongoDB that records all write operations. Enable the oplog on the primary server and ensure it has an adequate size to retain the required amount of historical data.

3. Create a custom application: Develop a custom application that connects to the MongoDB replica set and monitors the oplog for changes. You can use MongoDB's official drivers or libraries for your preferred programming language to interact with MongoDB.

4. Capture oplog changes: Continuously monitor the oplog and capture the changes made to the MongoDB database. The oplog will provide the necessary information about the write operations, including the modified documents and the corresponding collection.

5. Transform and route changes: As you capture the changes from the oplog, transform the data to match the structure of the MySQL database. Perform any necessary data conversions or mapping required to align the data between MongoDB and MySQL.

6. Connect to MySQL: Set up a connection to the MySQL database using the appropriate drivers or libraries available for your chosen programming language. Ensure you have the necessary credentials and access rights to write data to the MySQL database.

7. Write changes to MySQL: As you receive the transformed data from MongoDB, write it to the corresponding tables in the MySQL database. You can use SQL statements or an ORM (Object-Relational Mapping) library to perform the data insertion or update operations.

8. Handle conflicts and errors: Implement error handling mechanisms and address any conflicts that may arise during the replication process. For example, if a record already exists in MySQL, you may need to decide whether to update it, insert it as a new record, or handle conflicts in a custom manner.

9. Monitor and validate: Thoroughly test and monitor the replication process to ensure the accuracy and consistency of the data between MongoDB and MySQL. Monitor for any errors, performance issues, or data discrepancies and take appropriate actions to resolve them.