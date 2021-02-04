const functions = require('../../../../common/functions');
const config = require('../../../../config');
const validator = require('validator');
const statusCode = require('../../../../common/statusCode');
const message = require('../../../../common/message');
const fs = require('fs');
const db = require(`../user/database/${config.database}/${config.database}`);

class UserService {
  /**
   * API for user registration
   * @param {*} req (user details)
   * @param {*} res (json with success/failure)
   */
  async registration(info) {
    try {
      if (
        !validator.isEmail(info.email) ||
        validator.isEmpty(info.password) ||
        validator.isEmpty(info.gid) ||
        validator.isEmpty(info.full_name) ||
        validator.isEmpty(info.component)
      ) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.badRequest,
          data: null,
        };
      }

      const checkIfUserExists = await db.userDatabase().checkIfUserExists(info);

      if (checkIfUserExists.length > 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.duplicateDetails,
          data: null,
        };
      }

      info.password = functions.encryptPassword(info.password);

      const userRegistration = await db.userDatabase().userRegistration(info);

      let token = await functions.tokenEncrypt(info.email);
      token = Buffer.from(token, 'ascii').toString('hex');
      this.verifyEmail({ email: token });
      // let emailMessage = fs
      //   .readFileSync('./common/emailtemplate/welcome.html', 'utf8')
      //   .toString();
      // emailMessage = emailMessage
      //   .replace('$fullname', info.gid)
      //   .replace('$link', config.emailVerificationLink + token);

      // functions.sendEmail(
      //   info.email,
      //   message.registrationEmailSubject,
      //   emailMessage
      // );
      return {
        statusCode: statusCode.success,
        message: message.registration,
        data: userRegistration,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for email verification
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async verifyEmail(info) {
    try {
      if (!info.email) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.badRequest,
          data: null,
        };
      }
      const token = Buffer.from(info.email, 'hex').toString('ascii');
      const tokenDecrypt = await functions.tokenDecrypt(token);
      if (tokenDecrypt.message === 'jwt expired') {
        throw {
          statusCode: statusCode.unauthorized,
          message: message.emailLinkExpired,
          data: null,
        };
      }
      const verifyEmailDetails = await db
        .userDatabase()
        .verifyEmail(tokenDecrypt.data);
      return {
        statusCode: statusCode.success,
        message: message.emailVerificationSuccess,
        data: verifyEmailDetails,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for user login
   * @param {*} req (email address & password)
   * @param {*} res (json with success/failure)
   */
  async login(info) {
    try {
      if (validator.isEmpty(info.gid)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidLoginDetails,
          data: null,
        };
      }

      const loginDetails = await db.userDatabase().getUser(info.gid);

      if (loginDetails.length <= 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidLoginDetails,
          data: null,
        };
      }
      const password = functions.decryptPassword(loginDetails[0].password);
      if (password !== info.password) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidLoginDetails,
          data: null,
        };
      }

      if (loginDetails[0].isActive !== 1 || loginDetails[0].isDeleted !== 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.accountDisable,
          data: null,
        };
      }

      if (loginDetails[0].isEmailVerified === 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.emailVerify,
          data: null,
        };
      }

      const userDetails = {
        gid: loginDetails[0].gid,
        email: loginDetails[0].email,
        userId: loginDetails[0]._id,
      };

      const token = await functions.tokenEncrypt(userDetails);

      userDetails.token = token;

      return {
        statusCode: statusCode.success,
        message: message.success,
        data: userDetails,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API to Change password
   * @param {*} req (old password, token, new password )
   * @param {*} res (json with success/failure)
   */
  async changePassword(email, info) {
    try {
      if (
        validator.isEmpty(info.oldPassword) &&
        validator.isEmpty(info.newPassword)
      ) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.badRequest,
          data: null,
        };
      }

      const getPassword = await db.userDatabase().getPassword(email);

      if (getPassword.length <= 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidDetails,
          data: null,
        };
      }

      let password = functions.decryptPassword(getPassword[0].password);
      if (password !== info.oldPassword) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidPassword,
          data: null,
        };
      }

      // Encrypt password for the user
      password = functions.encryptPassword(info.newPassword);

      const updatePasswordDetails = await db
        .userDatabase()
        .updateUserPassword(email, password);

      return {
        statusCode: statusCode.success,
        message: message.passwordChanged,
        data: updatePasswordDetails,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for Forgot Password
   * @param {*} req (email address )
   * @param {*} res (json with success/failure)
   */
  async forgotPassword(info) {
    try {
      if (!validator.isEmail(info.email)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidEmail,
          data: null,
        };
      }
      const userDetail = await db.userDatabase().getUser(info.gid);

      if (userDetail.length <= 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidEmail,
          data: null,
        };
      }
      const to = userDetail[0].email;
      let token = await functions.tokenEncrypt(to);
      token = Buffer.from(token, 'ascii').toString('hex');
      const subject = message.forgotPasswordSubject;
      const link = config.resetPasswordLink + token;
      let emailMessage = fs
        .readFileSync('./common/emailtemplate/reset.html', 'utf8')
        .toString();
      emailMessage = emailMessage
        .replace('$fullname', userDetail[0].gid)
        .replace('$link', link)
        .replace('$emailId', config.supportEmail);

      functions.sendEmail(to, subject, emailMessage);
      return {
        statusCode: statusCode.success,
        message: message.resetLink,
        data: null,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for Reset Password
   * @param {*} req (email )
   * @param {*} res (json with success/failure)
   */
  async resetPassword(info) {
    try {
      if (
        validator.isEmpty(info.email) ||
        validator.isEmpty(info.newPassword)
      ) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidDetails,
          data: null,
        };
      }
      const email = Buffer.from(info.email, 'hex').toString('ascii');
      const emailAddressDetails = await functions.tokenDecrypt(email);
      if (!emailAddressDetails.data) {
        throw {
          statusCode: statusCode.unauthorized,
          message: message.emailLinkExpired,
          data: null,
        };
      }
      const password = functions.encryptPassword(info.newPassword);

      const passwordDetails = await db
        .userDatabase()
        .updateUserPassword(emailAddressDetails.data, password);

      return {
        statusCode: statusCode.success,
        message: message.passwordReset,
        data: passwordDetails,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for user history
   * @param {*} req (userId)
   * @param {*} res (json with success/failure)
   */
  async getProfile(gid) {
    try {
      const getProfileDetails = await db.userDatabase().getUser(gid);
      if (getProfileDetails.length > 0) {
        const userDetails = {
          gid: getProfileDetails[0].gid,
          email: getProfileDetails[0].email,
          component: getProfileDetails[0].component,
        };
        return {
          statusCode: statusCode.success,
          message: message.success,
          data: userDetails,
        };
      } else {
        return {
          statusCode: statusCode.bad_request,
          message: message.noData,
          data: null,
        };
      }
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API to update profile
   * @param {*} req (token, user information )
   * @param {*} res (json with success/failure)
   */
  async updateProfile(userId, info) {
    try {
      if (validator.isEmpty(info.gid)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.allFieldReq,
          data: null,
        };
      }

      const userDetail = await db.userDatabase().updateUser(userId, info);

      return {
        statusCode: statusCode.success,
        message: message.profileUpdate,
        data: userDetail,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * API for uploading user profile pic
   * @param {*} req (userId, base64 data)
   * @param {*} res (json with success/failure)
   */
  async addProfilePic(email, info) {
    try {
      var imageType = info.imageInfo.name
        ? info.imageInfo.name.split('.')[1]
        : '';
      if (!imageType) {
        throw {
          statusCode: statusCode.unsupported_media_type,
          message: message.invalidImage,
          data: [],
        };
      }

      const imageName = `profile-${Date.now()}`;
      const path = 'profile/';
      const imageInformation = {
        fileName: imageName,
        base64: info.imageInfo.base64,
        fileType: imageType,
        pathInfo: path,
      };
      const imageURLInfo = await functions.uploadFile(imageInformation);

      const imageURL = path + imageURLInfo.fileName;

      const addProfilePic = await db
        .userDatabase()
        .addProfilePic(email, imageURL);
      return {
        statusCode: statusCode.success,
        message: message.success,
        data: addProfilePic,
      };
    } catch (error) {
      throw {
        statusCode: error.statusCode,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }
}

module.exports = {
  userService: function () {
    return new UserService();
  },
};
