const object = require('./metadata');
const functions = require('../../../../common/functions');

const controller = {
  getDefaultParameters: async (req, res, next) => {
    try {
      const defaultParameters = await object.metadataService().getDefaultParameters();
      res.send(
        functions.responseGenerator(
          defaultParameters.statusCode,
          defaultParameters.message,
          defaultParameters.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  getScriptLastExecLog: async (req, res, next) => {
    try {
      const scriptLastExecLog = await object.metadataService().getScriptLastExecLog();
      res.send(
        functions.responseGenerator(
          scriptLastExecLog.statusCode,
          scriptLastExecLog.message,
          scriptLastExecLog.data
        )
      );
    } catch (error) {
      return next(error);
    }
  }
};

module.exports = controller;