/*****************************************************************************
 Filename:          main.ts
 Description:       Application Bootstrap

 Creation Date:     01/08/2019
 Author:            Piyush Gupte

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 *****************************************************************************/
import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store/store";
import vuetify from "./plugins/vuetify";
import * as moment from "moment";
import "@/common/style.css";
import Vuelidate from "vuelidate";
import EosHasAccess from "./components/security/has-access.vue";
import { userPermissions as userPermissionsMap } from "./common/user-permissions-map";

Vue.use(Vuelidate);
Vue.config.productionTip = false;

Vue.filter("fromMillis", (timeInMillis: number) => {
  return moment.default(timeInMillis).format("DD-MMMM-YYYY hh:mm:ss A");
});

export const EVENT_BUS = new Vue();
Vue.filter("capitalize", (value: any) => {
  if (value) {
    value = value.toString();
    return value.charAt(0).toUpperCase() + value.slice(1);
  }
});

// tslint:disable-next-line
Vue.prototype.$hasAccessToCsm = function (role: string) {
  if (!role) {
    return false;
  }
  const [resource, action] = role.split(":");
  const userPermissions = this.$store.getters["userLogin/getUserPermissions"];
  if (
    userPermissions &&
    userPermissions[resource] &&
    userPermissions[resource][action]
  ) {
    return true;
  }
  return false;
};

Vue.component("eos-has-access", EosHasAccess);

Vue.prototype.$eosUserPermissions = userPermissionsMap;

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App)
}).$mount("#app");
