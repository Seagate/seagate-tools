const config = require('../../../../config');
const validator = require('validator');
const statusCode = require('../../../../common/statusCode');
const message = require('../../../../common/message');
const db = require(`../component/database/${config.database}/${config.database}`);
const {
  validateSortingPagingOptions,
} = require('../../../../common/functions');

class ComponentService {
  /**
   * API for component registration
   * @param {*} req (component details)
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

      const checkIfComponentExists = await db
        .componentDatabase()
        .checkIfComponentExists(info);

      if (checkIfComponentExists.length > 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.duplicateComponentDetails,
          data: null,
        };
      }

      const componentRegistration = await db
        .componentDatabase()
        .componentRegistration(info);

      return {
        statusCode: statusCode.success,
        message: message.registration,
        data: componentRegistration,
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
   * API for component registration
   * @param {*} req (component details)
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
        data: componentRegistration,
      };
    } catch (error) {
      return error;
    }
  }

  /**
   * API for component getComponentInfo
   * @param {*} req (queryParams: limit, page, sortBy, orderBy)
   * @param {*} res (json with success/failure)
   */
  async getAllComponentInfo(queryParams) {
    try {
      const filters = validateSortingPagingOptions(queryParams);

      const componentDetails = await db
        .componentDatabase()
        .getAllComponent(filters);
      let response = {
        data: componentDetails,
        total_records: componentDetails.length,
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
   * API for component getComponentInfo
   * @param {*} req (id)
   * @param {*} res (json with success/failure)
   */
  async getComponentInfoById(id) {
    try {
      if (validator.isEmpty(id)) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidComponentDetails,
          data: null,
        };
      }

      const componentDetails = await db.componentDatabase().getComponent(id);

      if (componentDetails.length <= 0) {
        throw {
          statusCode: statusCode.bad_request,
          message: message.invalidComponentDetails,
          data: null,
        };
      }

      if (
        componentDetails[0].isActive !== 1 ||
        componentDetails[0].isDeleted !== 0
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
        data: componentDetails,
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
  componentService: function () {
    return new ComponentService();
  },
};
