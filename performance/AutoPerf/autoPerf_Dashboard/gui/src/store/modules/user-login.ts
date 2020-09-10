/*****************************************************************************
 Filename:          user-login.ts
 Description:       Create Root User and Login Store Module

 Creation Date:     08/11/2019
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
import { Api } from "./../../services/api";
import apiRegister from "./../../services/api-register";
import {
  Module,
  VuexModule,
  Mutation,
  Action,
  MutationAction
} from "vuex-module-decorators";
// import { userPermissions } from "./../../models/user-permissions";
Vue.use(Vuex);

@Module({
  namespaced: true
})
export default class UserLogin extends VuexModule {
  public user: any = {};
  public userPermissions: object = {};

  @Mutation
  public setUser(user: any) {
    this.user = user;
  }
  @Mutation
  public setUserPermissions(permissions: any) {
    this.userPermissions = permissions;
  }

  // Get user
  get getUser() {
    return this.user;
  }

  get getUserPermissions() {
    return this.userPermissions;
  }

  @Action
  public async logoutAction() {
    /*try {
      const res = await Api.post(apiRegister.logout, {});
      if (res && res.status) {
        return res.status;
      }
    } catch (e) {
      // tslint:disable-next-line: no-console
      console.log("err logger: ", e);
    }*/
    return 200;
  }
  @Action({ rawError: true })
  public async getUserPermissionsAction() {
    try {
      if (
        this.userPermissions &&
        !Object.entries(this.userPermissions).length
      ) {
        // const res = await Api.getAll(apiRegister.user_permissions);
        const res = await Api.getAll("");
        if (res && res.data && res.data.permissions) {
          this.context.commit("setUserPermissions", res.data.permissions);
          return res.data.permissions;
        }
      } else {
        return true;
      }
    } catch (e) {
      // tslint:disable-next-line: no-console
      console.error("err logger: ", e);
      throw new Error(e.message);
    }
  }
}
