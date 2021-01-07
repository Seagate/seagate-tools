const router = require('express').Router();
const api = require('./controller');
const auth = require('../../../../common/authentication');

// Middle layer for Manager API
router.post('/', auth.validateToken, auth.decryptRequest, api.registration);
router.get('/', api.getAllManager);
router.get('/:id', api.getManagerById);

module.exports = router;
