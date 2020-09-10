const { ScriptExecution } = require('./schema');
const { connection_failed } = require('../../../../../../common/statusCode');

class ScriptExecutionDatabase {

  async getAllScriptExecutionsByUserGID(user_gid) {
    try {
      const details = await ScriptExecution.find({ user_gid: user_gid }).sort([['start_time', -1]]);
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  async getScriptExecutionById(id) {
    try {
      const details = await ScriptExecution.findById(id);
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  async createScriptExecution(info) {
    const scriptExec = new ScriptExecution(info);
    try {
      const details = scriptExec.save();
      return details;
    } catch (error) {
      throw {
        statusCode: connection_failed,
        message: error.message,
        data: JSON.stringify(error),
      };
    }
  }

  async updateScriptExecution(id, log, isEnd=false) {
    try {
      const scriptExecObj = await ScriptExecution.findById(id);
      const updateObj = {log: scriptExecObj.log + log };
      if(isEnd) {
        updateObj.end_time = new Date().getTime();
      } 
      const details = await ScriptExecution.findByIdAndUpdate(id, {$set: updateObj});
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
  scriptExecutionDatabase: function () {
    return new ScriptExecutionDatabase();
  },
};
