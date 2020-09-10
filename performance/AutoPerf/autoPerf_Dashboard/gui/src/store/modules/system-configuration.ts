/*****************************************************************************
 Filename:          system-configuration.ts
 Description:       System Configuration Store Module

 Creation Date:     26/09/2019
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

Vue.use(Vuex);
@Module({
  namespaced: true
})
export default class SystemConfiguration extends VuexModule {
  public loaderShow: boolean = false;
  public loaderMessage: string = "";

  // Loader Config
  @Mutation
  public loaderConfigMutation(loaderData: any) {
    this.loaderShow = loaderData.show;
    this.loaderMessage = loaderData.message;
  }
  @Action
  public async showLoaderMessage(loaderData: any) {
    this.context.commit("loaderConfigMutation", loaderData);
  }
  @Action
  public async showLoader(message: string) {
    this.context.commit("loaderConfigMutation", {
      show: true,
      message
    });
  }

  @Action
  public async hideLoader() {
    this.context.commit("loaderConfigMutation", {
      show: false,
      message: ""
    });
  }
  get showLoaderStatus() {
    return this.loaderShow;
  }
  get loaderMessageText() {
    return this.loaderMessage;
  }
}
