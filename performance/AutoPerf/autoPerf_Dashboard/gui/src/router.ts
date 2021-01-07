/*****************************************************************************
 Filename:          router.ts
 Description:       Router

 Creation Date:     31/08/2020
 Author:            Shri Bhargav Metta

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 *****************************************************************************/
import Vue from "vue";
import Router from "vue-router";
import Dashboard from "./components/dashboard/dashboard.vue";
import EosDefault from "./components/eos-default.vue";
import EosUnauthorizedAccess from "./components/security/403.vue";
import EosNotFound from "./components/security/404.vue";

import AutoPerfLogin from "./components/account/login.vue";
import AutoPerfRegistration from "./components/account/registration.vue";

import store from "./store/store";

Vue.use(Router);

// Note: requiresAuth: Flag for User Logged into the system
const router = new Router({
  routes: [
    {
      path: "/login",
      name: "normal-login",
      component: AutoPerfLogin,
      meta: { requiresAuth: false }
    },
    {
      path: "/register",
      name: "registration",
      component: AutoPerfRegistration,
      meta: { requiresAuth: false }
    },
    {
      path: "/",
      component: EosDefault,
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          redirect: "dashboard"
        },
        {
          path: "dashboard",
          name: "dashboard",
          component: Dashboard,
          meta: {
            requiresAuth: true
          }
        },
        {
          path: "403",
          name: "403",
          component: EosUnauthorizedAccess,
          meta: { requiresAuth: true }
        }
      ]
    },
    { path: "*", component: EosNotFound }
  ]
});

// This code executes before any route happens
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    // This route requires auth, check if logged in
    // if not, redirect to login page.
    const conststr = require("./common/const-string.json");
    const token = localStorage.getItem(conststr.access_token);
    if (!token) {
      next({
        path: "/login"
      });
    } else {
      next();
    }
  } else {
    next(); // make sure to always call next()!
  }
});

export default router;
