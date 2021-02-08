var express = require('express');
var router = express.Router();
const db = require('../../common/database/mongoDB');

const userRouter = require('./modules/user/routes');
const componentRouter = require('./modules/component/routes');
const managerRouter = require('./modules/manager/routes');
const metadataRouter = require('./modules/metadata/routes');
const scriptExecutionRouter = require('./modules/script_execution/routes');

router.get('/', function (req, res) {
  res.send('Hello v1.0 GET API from Seagate');
});

router.get('/cleardb', function (req, res) {
  db.dropDatabase(function (err, result) {
    res.send(result);
  });
});

router.post('/', function (req, res) {
  res.send('Hello v1.0 POST API from Seagate');
});

router.use('/user', userRouter);
router.use('/component', componentRouter);
router.use('/manager', managerRouter);
router.use('/metadata', metadataRouter);
router.use('/script', scriptExecutionRouter);

module.exports = router;
