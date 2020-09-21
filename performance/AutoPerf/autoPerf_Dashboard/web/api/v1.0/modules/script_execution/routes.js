const router = require('express').Router();
const api = require('./controller');
const auth = require('../../../../common/authentication');

// Middle layer for Script execution API
router.get('/executions', auth.validateToken, auth.decryptRequest, api.getAllScriptExecutionsByUserGID);
router.get('/executions/:id', auth.validateToken, auth.decryptRequest, api.getScriptExecutionById);
router.post('/executions', auth.validateToken, auth.decryptRequest, api.createScriptExecution);

module.exports = router;
