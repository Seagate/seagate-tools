var express = require('express');
var router = express.Router();

/* GET home page. */
router.use('/', express.static('dist', { index: 'index.html' }));
// router.get('/', function (req, res, next) {
//   res.send('HW Allocation API from Seagate');
// });

module.exports = router;
