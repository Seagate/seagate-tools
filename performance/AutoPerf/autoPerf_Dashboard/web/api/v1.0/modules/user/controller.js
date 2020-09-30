const object = require('./user');
const functions = require('../../../../common/functions');

const controller = {
  //User Registration API
  registration: async (req, res, next) => {
    try {
      const registrationDetails = await object
        .userService()
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

  //Verify Email API
  verifyEmail: async (req, res, next) => {
    try {
      const verificationDetails = await object
        .userService()
        .verifyEmail(res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          verificationDetails.statusCode,
          verificationDetails.message,
          verificationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  //Login API
  login: async (req, res, next) => {
    try {
      const loginDetails = await object
        .userService()
        .login(res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          loginDetails.statusCode,
          loginDetails.message,
          loginDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Change Password API
  changePassword: async (req, res, next) => {
    try {
      const changePasswordDetails = await object
        .userService()
        .changePassword(res.locals.tokenInfo.email, res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          changePasswordDetails.statusCode,
          changePasswordDetails.message,
          changePasswordDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Forgot Password API
  forgotPassword: async (req, res, next) => {
    try {
      const forgotPasswordDetails = await object
        .userService()
        .forgotPassword(res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          forgotPasswordDetails.statusCode,
          forgotPasswordDetails.message,
          forgotPasswordDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Reset Password API
  resetPassword: async (req, res, next) => {
    try {
      const resetPasswordDetails = await object
        .userService()
        .resetPassword(res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          resetPasswordDetails.statusCode,
          resetPasswordDetails.message,
          resetPasswordDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Get Profile API
  getProfile: async (req, res, next) => {
    try {
      const userInformationDetails = await object
        .userService()
        .getProfile(res.locals.tokenInfo.gid);
      res.send(
        functions.responseGenerator(
          userInformationDetails.statusCode,
          userInformationDetails.message,
          userInformationDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Update Profile API
  updateProfile: async (req, res, next) => {
    try {
      const updateProfileDetails = await object
        .userService()
        .updateProfile(res.locals.tokenInfo.gid, res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          updateProfileDetails.statusCode,
          updateProfileDetails.message,
          updateProfileDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },

  // Add profile picture
  profilePic: async (req, res, next) => {
    try {
      const profilePicDetails = await object
        .userService()
        .addProfilePic(res.locals.tokenInfo.email, res.locals.requestedData);
      res.send(
        functions.responseGenerator(
          profilePicDetails.statusCode,
          profilePicDetails.message,
          profilePicDetails.data
        )
      );
    } catch (error) {
      return next(error);
    }
  },
};

module.exports = controller;
