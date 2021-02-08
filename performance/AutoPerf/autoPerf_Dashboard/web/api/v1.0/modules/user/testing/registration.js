const mocha = require('mocha');
const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
const user = require('../user');
const app = require('../../../app');
const should = chai.should();
const message = require('../../common/message');

describe('User Module', () => {
  describe('"Registration functionality"', () => {
    //Checking whether the functionality is being export
    it('should export a function', () => {
      expect(user.userService().registration).to.be.a('function');
    });

    it('should return a promise', () => {
      const checkPromise = user.userService().registration();
      expect(checkPromise.then).to.be.a('function');
      expect(checkPromise.catch).to.be.a('function');
    });

    it('should return a failure', async () => {
      const info = {
        gid: 'Temp User',
        email: 'abc@test.com',
        password: '12345678',
        component: '+919999999999',
      };
      const registrationDetails = await user.userService().registration(info);
      console.log('Error: ', registrationDetails.message);
      if (
        registrationDetails.message === message.invalidDetails ||
        registrationDetails.message === message.duplicateDetails
      ) {
        expect(registrationDetails.statusCode).to.be.equal('01');
      } else {
        expect(registrationDetails.statusCode).to.be.equal('04');
      }
    });

    it('Checking functionality with proper data', async () => {
      const info = {
        gid: 'Temp User',
        password: '12345678',
        email: 'abc@test.com',
        component: '+919999999999',
      };
      const registrationDetails = await user.userService().registration(info);
      expect(registrationDetails.statusCode).to.be.equal('00');
      expect(registrationDetails.data).to.be.a('object');
    });
  });
});

// Need to study
// it('Should success if correct information is provided through API call', done => {
//   request(app)
//     .post('/api/user/registration')
//     .send({
//       gid: 'Temp User',
//       password: '12345678',
//       email: 'abc@test.com',
//       component: '+919999999999'
//     })
//     .end((err, res) => {
//       res.body.statusCode.should.be.equal('00');
//       res.body.should.have.property('message');
//     });
//   done();
// });
