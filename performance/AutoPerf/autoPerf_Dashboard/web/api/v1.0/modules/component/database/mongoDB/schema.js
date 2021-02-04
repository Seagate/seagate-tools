const mongoose = require('mongoose');

const componentSchema = new mongoose.Schema({
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

const Component = mongoose.model('Component', componentSchema, 'components');
module.exports = {
  Component,
  componentSchema,
};
