const mocha = require('mocha');
const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
const user = require('../user');
const app = require('../../../app');
const should = chai.should();
const message = require('../../common/message');

describe('User Module', () => {
  describe('"Verify Email functionality"', () => {
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
        email: '',
      };
      const verifyEmail = await user.userService().verifyEmail(info);
      console.log('Error: ', verifyEmail.message);
      if (verifyEmail.message === message.badRequest) {
        expect(verifyEmail.statusCode).to.be.equal('01');
      } else {
        expect(verifyEmail.statusCode).to.be.equal('04');
      }
    });

    it('should return a success', async () => {
      const info = {
        email:
          '65794a68624763694f694a49557a49314e694973496e523563434936496b705856434a392e65794a6b59585268496a6f69633268686157746f4c6d31315a47526863334e68636a68415a32316861577775593239744969776961574630496a6f784e5459314d4441344d5467794c434a6c654841694f6a45314e6a55774f5451314f444a392e745f7275653749426338565f3061527277686f5241764c4b4b66756f37356d6d566a766f33577077744e6b',
      };
      const verifyEmail = await user.userService().verifyEmail(info);
      console.log('Success: ', verifyEmail.message);
      expect(verifyEmail.statusCode).to.be.equal('00');
    });
  });
});
