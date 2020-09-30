const router = require('express').Router();
const api = require('./controller');
const auth = require('../../../../common/authentication');

// Middle layer for Metadata API
router.get('/default_parameters', auth.validateToken, auth.decryptRequest, api.getDefaultParameters);
router.get('/last_execution_log', auth.validateToken, auth.decryptRequest, api.getScriptLastExecLog);

module.exports = router;
