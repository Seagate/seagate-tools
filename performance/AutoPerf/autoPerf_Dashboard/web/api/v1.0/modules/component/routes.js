const router = require('express').Router();
const api = require('./controller');
const auth = require('../../../../common/authentication');

// Middle layer for Component API
router.post('/', auth.validateToken, auth.decryptRequest, api.registration);
router.get('/', api.getAllComponent);
router.get('/:id', api.getComponentById);

module.exports = router;
