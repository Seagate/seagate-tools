const mongoose = require('mongoose');

const scriptExecutionSchema = new mongoose.Schema({
  user_gid: {
    type: String,
    required: true
  },
  log: {
    type: String,
    default: ""
  },
  start_time: {
    type: Number,
    default: 0
  },
  end_time: {
    type: Number,
    default: 0
  },
});

const ScriptExecution = mongoose.model('ScriptExection', scriptExecutionSchema, 'script_execution');
module.exports = {
  ScriptExecution,
  scriptExecutionSchema,
};
