const mocha = require('mocha');
const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
const user = require('../user');
const app = require('../../../app');
const should = chai.should();
const message = require('../../common/message');

describe('User Module', () => {
  describe('"Forgot Password functionality"', () => {
    //Checking whether the functionality is being export
    it('should export a function', () => {
      expect(user.userService().forgotPassword).to.be.a('function');
    });

    it('should return a promise', () => {
      const checkPromise = user.userService().forgotPassword();
      expect(checkPromise.then).to.be.a('function');
      expect(checkPromise.catch).to.be.a('function');
    });

    it('should return a failure', async () => {
      const info = {
        email: '',
      };
      const forgotPassword = await user.userService().forgotPassword(info);
      console.log('Error: ', forgotPassword.message);
      if (forgotPassword.message === message.invalidEmail) {
        expect(forgotPassword.statusCode).to.be.equal('01');
      } else {
        expect(forgotPassword.statusCode).to.be.equal('04');
      }
    });

    it('should return a success', async () => {
      const info = {
        email: 'abc@test.com',
      };
      const forgotPassword = await user.userService().forgotPassword(info);
      console.log('Success: ', forgotPassword.message);
      expect(forgotPassword.statusCode).to.be.equal('00');
    });
  });
});
