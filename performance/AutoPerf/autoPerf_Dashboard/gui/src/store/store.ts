/*****************************************************************************
 Filename:          store.ts
 Description:       Root Store

 Creation Date:     30/08/2019
 Author:            Sanjeevan Bhave

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 *****************************************************************************/
import Vue from "vue";
import Vuex from "vuex";
import userLogin from "./modules/user-login";
import systemConfig from "./modules/system-configuration";
import messageDialog from "./modules/message-dialog";
import alertNotification from "./modules/alert-notification";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    userLogin,
    systemConfig,
    messageDialog,
    alertNotification
  }
});
