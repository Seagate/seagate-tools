const object = require('./manager');
const functions = require('../../../../common/functions');

const controller = {
  //Manager Registration API
  registration: async (req, res, next) => {
    try {
      const registrationDetails = await object
        .managerService()
        .registration(res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          registrationDetails.statusCode,
          registrationDetails.message,
          registrationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Get Manager API
  getAllManager: async (req, res, next) => {
    try {
      const managerInformationDetails = await object
        .managerService()
        .getAllManagerInfo(req.query);
      res.send(
        functions.responseGenerator(
          managerInformationDetails.statusCode,
          managerInformationDetails.message,
          managerInformationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Get Manager API
  getManagerById: async (req, res, next) => {
    try {
      const managerInformationDetails = await object
        .managerService()
        .getManagerInfoById(req.params.id);
      res.send(
        functions.responseGenerator(
          managerInformationDetails.statusCode,
          managerInformationDetails.message,
          managerInformationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },
};

module.exports = controller;
