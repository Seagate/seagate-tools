const object = require('./script_execution');
const functions = require('../../../../common/functions');

const controller = {
  getAllScriptExecutionsByUserGID: async (req, res, next) => {
    try {
      const result = await object.scriptExecutionService().getAllScriptExecutionsByUserGID(req.query.user_gid);
      res.send(
        functions.responseGenerator(
          result.statusCode,
          result.message,
          result.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  getScriptExecutionById: async (req, res, next) => {
    try {
      const scriptLastExecLog = await object.scriptExecutionService().getScriptExecutionById(req.params.id);
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
  },

  createScriptExecution: async (req, res, next) => {
    try {
      const scriptLastExecLog = await object.scriptExecutionService()
                                            .createScriptExecution(res.locals.tokenInfo.gid, res.locals.requestedData.script_args);
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