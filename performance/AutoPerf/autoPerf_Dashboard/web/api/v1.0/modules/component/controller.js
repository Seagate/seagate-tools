const object = require('./component');
const functions = require('../../../../common/functions');

const controller = {
  //Component Registration API
  registration: async (req, res, next) => {
    try {
      const registrationDetails = await object
        .componentService()
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

  // Get Component API
  getAllComponent: async (req, res, next) => {
    try {
      const componentInformationDetails = await object
        .componentService()
        .getAllComponentInfo(req.query);
      res.send(
        functions.responseGenerator(
          componentInformationDetails.statusCode,
          componentInformationDetails.message,
          componentInformationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Get Component API
  getComponentById: async (req, res, next) => {
    try {
      const componentInformationDetails = await object
        .componentService()
        .getComponentInfoById(req.params.id);
      res.send(
        functions.responseGenerator(
          componentInformationDetails.statusCode,
          componentInformationDetails.message,
          componentInformationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },
};

module.exports = controller;
