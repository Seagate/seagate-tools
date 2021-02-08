const mocha = require('mocha');
const request = require('supertest');
const chai = require('chai');
const chaiHttp = require('chai-http');
const expect = chai.expect;
const user = require('../user');
const app = require('../../../../../app');
const should = chai.should();
const message = require('../../../../../common/message');
chai.use(chaiHttp);

describe('User Module', () => {
  describe('"login functionality"', () => {
    // Checking whether the functionality is being export
    it('should export a function', () => {
      expect(user.userService().login).to.be.a('function');
    });

    // Checking whether the functionality return promise
    it('should return a promise', () => {
      const checkPromiseResult = user.userService().login();
      expect(checkPromiseResult.then).to.be.a('Function');
      expect(checkPromiseResult.catch).to.be.a('Function');
    });

    it('should return a failure', async () => {
      const loginDetails = await user.userService().login({
        email: 'abc@test.com',
        password: '12345678',
      });
      if (
        loginDetails.message === message.invalidLoginDetails ||
        loginDetails.message === message.accountDisable ||
        loginDetails.message === message.emailVerify
      ) {
        expect(loginDetails.statusCode).to.be.equal('01');
      } else {
        console.log(loginDetails.message);
        expect(loginDetails.statusCode).to.be.equal('04');
      }
    });

    it('should return a success if credential is valid', async () => {
      const loginDetails = await user.userService().login({
        email: 'abc@test.com',
        password: '123456789',
      });
      expect(loginDetails.statusCode).to.be.equal('00');
    });

    it('should return success while calling from API', () => {
      return chai
        .request(app)
        .post('/api/user/login')
        .send({
          email: 'abc@test.com',
          password: '123456789',
        })
        .then((res) => {
          expect(res.status).to.be.equal(200);
          expect(res.body.statusCode).to.be.equal('00');
        });
    });
  });
});
