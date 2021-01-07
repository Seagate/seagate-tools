const { Component } = require('./schema');
const { connection_failed } = require('../../../../../../common/statusCode');

class ComponentDatabase {
  /**
   * Database call to check if component exists
   * @param {*} req (component)
   * @param {*} res (json with success/failure)
   */
  async checkIfComponentExists(info) {
    try {
      const details = await Component.find({
        name: info.name,
      });
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * Database call for inserting component information
   * @param {*} req (component details)
   * @param {*} res (json with success/failure)
   */
  async componentRegistration(info) {
    const component = new Component(info);
    try {
      const details = await component.save();
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }
  /**
   * Database call for selecting component details for getComponentInfo
   * @param {*} req (filters)
   * @param {*} res (json with success/failure)
   */
  async getAllComponent(filters) {
    try {
      const details = await Component.find({})
        .limit(filters.limit)
        .skip(filters.skip)
        .sort(filters.sortOptions)
        .populate('components');
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * Database call for selecting component details for getComponentInfo
   * @param {*} req (id)
   * @param {*} res (json with success/failure)
   */
  async getComponent(id) {
    try {
      const details = await Component.find({ _id: id });
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  /**
   * Database call for inserting component information
   * @param {*} req (component details)
   * @param {*} res (json with success/failure)
   */
  async componentRegistrationBulk(info) {
    try {
      const details = await Component.insertMany(info);
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }
}

module.exports = {
  componentDatabase: function () {
    return new ComponentDatabase();
  },
};
