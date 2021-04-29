const router = require('express').Router();
const api = require('./controller');
const auth = require('../../../../common/authentication');

// Middle layer for Metadata API
router.get('/default_parameters', auth.validateToken, auth.decryptRequest, api.getDefaultParameters);
router.get('/last_execution_log', auth.validateToken, auth.decryptRequest, api.getScriptLastExecLog);
router.post('/node', auth.validateToken, auth.decryptRequest, api.addNode);
router.post('/client', auth.validateToken, auth.decryptRequest, api.addClient);

module.exports = router;
