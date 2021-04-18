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
  },

  addNode: async (req, res, next) => {
    try {
      const addNodeResult = await object.metadataService()
                                            .addNode(res.locals.tokenInfo.gid, res.locals.requestedData.node);
      res.send(
        functions.responseGenerator(
          addNodeResult.statusCode,
          addNodeResult.message,
          addNodeResult.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  addClient: async (req, res, next) => {
    try {
      const addClientResult = await object.metadataService()
                                            .addClient(res.locals.tokenInfo.gid, res.locals.requestedData.client);
      res.send(
        functions.responseGenerator(
          addClientResult.statusCode,
          addClientResult.message,
          addClientResult.data
        )
      );
    } catch (error) {
      return next(error);
    }
  }
};

module.exports = controller;