const sql = require('mssql');
const config = require('../../config');

const connection = new sql.ConnectionPool({
  user: config.databaseUser,
  password: config.databasePassword,
  server: config.databaseHost,
  database: config.databaseName,
  options: {
    encrypt: true,
  },
});

connection.connect();

var con = new sql.Request(connection);

sql.connect(config, function (err) {
  if (err) {
    console.log('Error connecting to Database');
    return;
  }
  console.log(
    'Connection established to Host - [' +
      config.databaseHost +
      '] DB - [' +
      config.databaseName +
      ']'
  );
});

module.exports = con;
