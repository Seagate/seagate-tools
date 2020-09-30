const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
require('./common/database/mongoDB');
const rateLimit = require('express-rate-limit');
const winston = require('./common/winston');
const { errorHandlerMiddleware, errorHandler } = require('./common/error');
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');
// require('./services/app-init-bulk-insert');

// view engine setup
app.set('views', path.join(__dirname, 'views'));

// HTTP request logger middleware for node.js
app.use(morgan('combined', { stream: winston.stream }));

/**
 * Parse incoming request bodies in a middleware before your handlers,
 * available under the req.body property.
 */
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// Parse Cookie header and populate req.cookies
app.use(cookieParser());

/**
 * CORS is a node.js package for providing a Connect/Express middleware
 * that can be used to enable CORS with various options.
 */
app.use(cors());

app.use(express.static(path.join(__dirname, 'public')));

/**
 * apply to all requests
 * Note - Rate Limiter can be applied to any individual API also. For more information
 * Please visit https://www.npmjs.com/package/express-rate-limit
 */
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
  })
);

// API Calling
app.use('/', require('./routes'));
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
app.use('/api', require('./api'));

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

process.on('uncaughtException', function (err) {
  errorHandler(err);
});

// error handler
app.use(function (err, req, res, next) {
  errorHandlerMiddleware(err, req, res);
});

module.exports = app;
