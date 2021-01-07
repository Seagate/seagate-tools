const mongoose = require('mongoose');
const { mongoDBConnectionString } = require('../../config');

mongoose.connect(mongoDBConnectionString, {
  useUnifiedTopology: true,
  useCreateIndex: true,
  useNewUrlParser: true,
  useFindAndModify: true
});

const db = mongoose.connection;
// const db = mongoose.createConnection(mongoDBConnectionString);

db.on('error', function (err) {
  console.log('Mongoose connection error: ' + err);
});

db.on('connected', function () {
  console.log('Mongoose connected ');
});

db.on('disconnected', function () {
  console.log('Mongoose disconnected');
});

//export the module
module.exports = db;
