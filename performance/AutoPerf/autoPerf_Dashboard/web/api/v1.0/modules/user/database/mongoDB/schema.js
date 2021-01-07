const mongoose = require('mongoose');

const userSchema = mongoose.Schema(
  {
    gid: {
      type: String,
      required: true,
      unique: true,
    },
    full_name: {
      type: String,
      required: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      validate: {
        validator: (text) => {
          if (text !== null && text.length > 0) {
            const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(text);
          }
          return false;
        },
        message: 'Invalid email address',
      },
    },
    component: {
      type: String,
      required: true,
    },
    team_name: {
      type: String,
    },
    manager_name: {
      type: String,
    },
    role: {
      type: String,
    },
    password: {
      type: String,
      required: true,
    },
    isEmailVerified: {
      type: Number,
      default: 0,
    },
    isActive: {
      type: Number,
      default: 1,
    },
    isDeleted: {
      type: Number,
      default: 0,
    },
  },
  { timestamps: true, collection: 'users' }
);

const User = mongoose.model('User', userSchema);

module.exports = User;
