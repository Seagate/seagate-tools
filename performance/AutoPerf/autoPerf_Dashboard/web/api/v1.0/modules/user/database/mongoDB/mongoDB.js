const User = require('./schema');
const { connection_failed } = require('../../../../../../common/statusCode');

class UserDatabase {
  /**
   * Database call to check if user exists
   * @param {*} req (email address & component)
   * @param {*} res (json with success/failure)
   */
  async checkIfUserExists(info) {
    try {
      const details = await User.find({
        $or: [
          {
            email: info.email,
          },
          {
            gid: info.gid,
          },
        ],
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
   * Database call for inserting user information
   * @param {*} req (user details)
   * @param {*} res (json with success/failure)
   */
  async userRegistration(info) {
    const user = new User(info);
    try {
      const details = await user.save();
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
      const details = await User.updateOne(
        { email: email },
        { isEmailVerified: 1 }
      );
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
   * @param {*} req (gid)
   * @param {*} res (json with success/failure)
   */
  async getUser(gid) {
    try {
      const details = await User.find(
        { gid },
        {
          gid: 1,
          full_name: 1,
          email: 1,
          password: 1,
          component: 1,
          team_name: 1,
          manager_name: 1,
          role: 1,
          isEmailVerified: 1,
          isActive: 1,
          isDeleted: 1,
        }
      );
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
      const details = await User.find(
        { email: email },
        {
          password: 1,
        }
      );
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
   * Database call for updating userpassword
   * @param {*} req (email)
   * @param {*} res (json with success/failure)
   */
  async updateUserPassword(email, password) {
    try {
      const details = await User.updateOne(
        { email: email },
        { password: password }
      );
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
      const details = await User.updateOne({ email: email }, { gid: info.gid });
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
      const details = await User.updateOne(
        { email: email },
        { profileURL: path }
      );
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
