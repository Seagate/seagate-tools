/*****************************************************************************
 Filename:          alertsNotification.ts
 Description:       Alert Notification Store

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
import { Api } from "./../../services/api";
import apiRegister from "./../../services/api-register";
Vue.use(Vuex);

// Interface for CSM schema for Alert
export interface AlertInfo {
    time: string;
    alert_type: string;
    status: string;
    location: string;
    healthReason: string;
    comment: string;
    Acknowledge: boolean;
    Resolved: boolean;
}

export default {
    state: {
        // all websockets related state data will be stored in socket state object
        socket: {
            alerts: Array<AlertInfo>(),
            alertCount: 0
        }
    },
    getters: {
    },
    mutations: {
        // will get called when web-socket connection is opened
        SOCKET_ONOPEN(state: any, event: any) {
            Vue.prototype.$socket = event.currentTarget;
        },
        // will get called when web-socket connection is clossed
        SOCKET_ONCLOSE(state: any) {
            return;
        },
        // will get called when error occors in web-socket connection
        SOCKET_ONERROR(state: any, event: any) {
            return;
        },
        // will get called when we recives messages on web-sockets layer
        SOCKET_ONMESSAGE(state: any, message: any) {
            // state.socket.alerts.unshift(message);
            // state.socket.alertCount++;
            // console.log(message);
        },
        // will get called on web-socket connection reconnect event.
        SOCKET_RECONNECT(state: any, count: any) {
            return;
        },
        // will get called on web-sockets reconnection error.
        SOCKET_RECONNECT_ERROR(state: any) {
            return;
        },
        apiNotification(state: any, list: any) {
            // tslint:disable-next-line: prefer-for-of
            for (let alertCount = 0; alertCount < list.alerts.length; alertCount++) {
                state.socket.alerts.push(list.alerts[alertCount]);
            }
            state.socket.alertCount = list.total_records;
        }
    },
    actions: {
        async alertDataAction(context: any) {
            const queryParams = {
                sortby: "created_time",
                dir: "desc",
                offset: 1,
                limit: 5,
                acknowledged: false,
                resolved: false
            };
            try {
                const res = await Api.getAll("", queryParams);
                const data = res.data;
                context.commit("apiNotification", data);
            } catch (e) {
                // tslint:disable-next-line: no-console
                console.log("err logger: ", e);
            }
        }
    }
};
