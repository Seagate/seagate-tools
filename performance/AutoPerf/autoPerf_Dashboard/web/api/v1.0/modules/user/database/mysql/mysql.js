const con = require('../../../../../../common/database/mysql');
const util = require('util');
const query = util.promisify(con.query).bind(con);
const { databaseInitial } = require('../../../../../../config');
const { connection_failed } = require('../../../../../../common/statusCode');

class UserDatabase {
  /**
   * Database call to check if user exists
   * @param {*} req (email address & component)
   * @param {*} res (json with success/failure)
   */
  async checkIfUserExists(info) {
    try {
      const sqlSelectQuery = `SELECT * FROM ${databaseInitial}user WHERE email = ? OR component = ?`;
      const details = await query(sqlSelectQuery, [info.email, info.component]);
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
   * Database call for inserting user information
   * @param {*} req (user details)
   * @param {*} res (json with success/failure)
   */
  async userRegistration(info) {
    try {
      const sqlInsertQuery = `INSERT INTO ${databaseInitial}user(gid, email, password, component) VALUES (?, ?, ?, ?)`;
      const details = await query(sqlInsertQuery, [
        info.gid,
        info.email,
        info.password,
        info.component,
      ]);
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
   * Database call for updating the user email verification
   * @param {*} req (email address)
   * @param {*} res (json with success/failure)
   */
  async verifyEmail(email) {
    try {
      const sqlUpdateQuery = `UPDATE ${databaseInitial}user SET isEmailVerified = 1 WHERE email = ?`;
      const details = await query(sqlUpdateQuery, [email]);
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
   * Database call for selecting user details for login
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async getUser(email) {
    try {
      const sqlSelectQuery = `
        SELECT id, gid, email, password, component, isEmailVerified, isActive, isDeleted 
        FROM ${databaseInitial}user 
        WHERE email = ?`;
      const details = await query(sqlSelectQuery, [email]);
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
   * Database call for selecting userpassword for changing password
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async getPassword(email) {
    try {
      const sqlSelectQuery = `SELECT password FROM ${databaseInitial}user WHERE email = ?`;
      const details = await query(sqlSelectQuery, [email]);
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
   * Database call for updating userpassword by email address
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async updateUserPassword(email, password) {
    try {
      const sqlUpdateQuery = `UPDATE ${databaseInitial}user SET password = ? WHERE email = ?`;
      const details = await query(sqlUpdateQuery, [password, email]);
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
   * Database call for updating userdetails
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async updateUser(email, info) {
    try {
      const sqlUpdateQuery = `UPDATE ${databaseInitial}user SET gid = ? WHERE email = ?`;
      const details = await query(sqlUpdateQuery, [info.gid, email]);
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
   * Database call for updating userdetails
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async addProfilePic(email, path) {
    try {
      const sqlUpdateQuery = `UPDATE ${databaseInitial}user SET profileURL = ? WHERE email = ?`;
      const details = await query(sqlUpdateQuery, [path, email]);
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
  userDatabase: function () {
    return new UserDatabase();
  },
};
