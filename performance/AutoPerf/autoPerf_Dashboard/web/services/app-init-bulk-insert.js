const db = require('../common/database/mongoDB');
const { hardwareService } = require('../api/v1.0/modules/hardware/hardware');
const { hardwareList } = require('../common/models/hardware-list');
const {
  hardwareTypeService,
} = require('../api/v1.0/modules/hardware-type/hardware-type');
const { hardwareTypeList } = require('../common/models/hardware-type-list');

db.on('connected', async function () {
  try {
    await hardwareService().registrationBulk(hardwareList);
    await hardwareTypeService().registrationBulk(hardwareTypeList);
    console.log('Hardwares and Hardware types inserted successfully.');
  } catch (error) {
    console.log('Hardwares and Hardware types insert failed.');
  }
});
