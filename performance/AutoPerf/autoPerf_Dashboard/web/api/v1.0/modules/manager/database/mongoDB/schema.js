const mongoose = require('mongoose');

const managerSchema = new mongoose.Schema({
  name: {
    type: String,
    unique: true,
    required: true,
  },
  isActive: {
    type: Number,
    default: 1,
  },
  isDeleted: {
    type: Number,
    default: 0,
  },
});

const Manager = mongoose.model('Manager', managerSchema, 'managers');
module.exports = {
  Manager,
  managerSchema,
};
