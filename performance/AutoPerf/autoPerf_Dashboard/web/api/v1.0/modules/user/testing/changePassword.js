const mocha = require('mocha');
const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
const user = require('../user');
const app = require('../../../app');
const should = chai.should();
const message = require('../../common/message');

describe('User Module', () => {
  describe('"Change Password functionality"', () => {
    //Checking whether the functionality is being export
    it('should export a function', () => {
      expect(user.userService().verifyEmail).to.be.a('function');
    });

    it('should return a promise', () => {
      const checkPromise = user.userService().verifyEmail();
      expect(checkPromise.then).to.be.a('function');
      expect(checkPromise.catch).to.be.a('function');
    });

    it('should return a failure', async () => {
      const info = {
        oldPassword: '',
        newPassword: '',
      };
      const changePassword = await user.userService().changePassword(1, info);
      console.log('Error: ', changePassword.message);
      if (
        changePassword.message === message.badRequest ||
        changePassword.message === message.invalidDetails ||
        changePassword.message === message.invalidPassword
      ) {
        expect(changePassword.statusCode).to.be.equal('01');
      } else {
        expect(changePassword.statusCode).to.be.equal('04');
      }
    });

    it('should return a success', async () => {
      const info = {
        oldPassword: '12345678',
        newPassword: '123456789',
      };
      const changePassword = await user.userService().changePassword(1, info);
      console.log('Success: ', changePassword.message);
      expect(changePassword.statusCode).to.be.equal('00');
    });
  });
});
