// MYSQL Database file

const mysql = require('mysql');
const config = require('../../config');

const con = mysql.createPool({
  connectionLimit: 10,
  host: config.databaseHost,
  user: config.databaseUser,
  password: config.databasePassword,
  database: config.databaseName,
  port: config.databasePort,
});

con.getConnection(function (err, connection) {
  if (err) {
    console.log(err);
    console.log('Error connecting to Database');
    return;
  }
  console.log('Connection established');
});

module.exports = con;
