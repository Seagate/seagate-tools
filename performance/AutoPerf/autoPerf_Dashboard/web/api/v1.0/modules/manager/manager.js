const config = require('../../../../config');
const validator = require('validator');
const statusCode = require('../../../../common/statusCode');
const message = require('../../../../common/message');
const db = require(`../manager/database/${config.database}/${config.database}`);
const {
  validateSortingPagingOptions,
} = require('../../../../common/functions');

class ManagerService {
  /**
   * API for manager registration
   * @param {*} req (manager details)
   * @param {*} res (json with success/failure)
   */
  async registration(info) {
    try {
      if (validator.isEmpty(info.name)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.badRequest,
          data: null,
        };
      }

      const checkIfManagerExists = await db
        .managerDatabase()
        .checkIfManagerExists(info);

      if (checkIfManagerExists.length > 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.duplicateManagerDetails,
          data: null,
        };
      }

      const managerRegistration = await db
        .managerDatabase()
        .managerRegistration(info);

      return {
        statusCode: statusCode.success,
        message: message.registration,
        data: managerRegistration,
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
   * API for manager registration
   * @param {*} req (manager details)
   * @param {*} res (json with success/failure)
   */
  async registrationBulk(info) {
    try {
      const promises = info.map(async (e) => {
        try {
          return await this.registration(e);
        } catch (error) {
          return error;
        }
      });
      await Promise.all(promises);
      return {
        statusCode: statusCode.success,
        message: message.registration,
        data: managerRegistration,
      };
    } catch (error) {
      return error;
    }
  }

  /**
   * API for manager getManagerInfo
   * @param {*} req (queryParams: limit, page, sortBy, orderBy)
   * @param {*} res (json with success/failure)
   */
  async getAllManagerInfo(queryParams) {
    try {
      const filters = validateSortingPagingOptions(queryParams);

      const managerDetails = await db.managerDatabase().getAllManager(filters);

      let response = {
        data: managerDetails,
        total_records: managerDetails.length,
      };
      return {
        statusCode: statusCode.success,
        message: message.success,
        data: response,
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
   * API for manager getManagerInfo
   * @param {*} req (id)
   * @param {*} res (json with success/failure)
   */
  async getManagerInfoById(id) {
    try {
      if (validator.isEmpty(id)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidManagerDetails,
          data: null,
        };
      }

      const managerDetails = await db.managerDatabase().getManager(id);

      if (managerDetails.length <= 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidManagerDetails,
          data: null,
        };
      }

      if (
        managerDetails[0].isActive !== 1 ||
        managerDetails[0].isDeleted !== 0
      ) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.accountDisable,
          data: null,
        };
      }

      return {
        statusCode: statusCode.success,
        message: message.success,
        data: managerDetails,
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
  managerService: function () {
    return new ManagerService();
  },
};
