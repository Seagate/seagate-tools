const { Manager } = require('./schema');
const { connection_failed } = require('../../../../../../common/statusCode');

class ManagerDatabase {
  /**
   * Database call to check if manager exists
   * @param {*} req (manager)
   * @param {*} res (json with success/failure)
   */
  async checkIfManagerExists(info) {
    try {
      const details = await Manager.find({
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
   * Database call for inserting manager information
   * @param {*} req (manager details)
   * @param {*} res (json with success/failure)
   */
  async managerRegistration(info) {
    const manager = new Manager(info);
    try {
      const details = await manager.save();
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
   * Database call for selecting manager details for getManagerInfo
   * @param {*} req (filters)
   * @param {*} res (json with success/failure)
   */
  async getAllManager(filters) {
    try {
      const details = await Manager.find({})
        .limit(filters.limit)
        .skip(filters.skip)
        .sort(filters.sortOptions)
        .populate('managers');
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
   * Database call for selecting manager details for getManagerInfo
   * @param {*} req (id)
   * @param {*} res (json with success/failure)
   */
  async getManager(id) {
    try {
      const details = await Manager.find({ _id: id });
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
   * Database call for inserting manager information
   * @param {*} req (manager details)
   * @param {*} res (json with success/failure)
   */
  async managerRegistrationBulk(info) {
    try {
      const details = await Manager.insertMany(info);
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
  managerDatabase: function () {
    return new ManagerDatabase();
  },
};
