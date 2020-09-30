// const { responseGenerator } = require('./functions');
const winston = require('./winston');

const errorHandlerMiddleware = (error, req, res) => {
  winston.error(
    `${error.statusCode || 500} - ${error.message} - ${error.data} - ${
      req.originalUrl
    } - ${req.method} - ${req.ip}`
  );

  res.send(
    require('./functions').responseGenerator(
      error.statusCode,
      error.message,
      error.data
    )
  );
};

function errorHandler(error) {
  winston.error(`${JSON.stringify(error)}`);
}

module.exports = {
  errorHandlerMiddleware,
  errorHandler,
};
