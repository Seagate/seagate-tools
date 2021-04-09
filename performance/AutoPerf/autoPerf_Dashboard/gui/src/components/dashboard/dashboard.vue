<template>
  <div class="dashboard-padding">
    <v-row>
      <v-col col="12" md="3" sm="5">
        <v-card>
          <v-toolbar color="#6ebe49" dense>
            <span style="color: #ffffff; font-size: 18px">Run Script</span>
            <v-spacer></v-spacer>
            <v-btn
              style="margin-right: 10px"
              :href="graphanaURL"
              target="_blank"
              v-bind:disabled="!selectedParameters.client"
              color="#ffffff"
              small
              outlined
              >Grafana</v-btn
            >
            <v-btn small color="#ffffff" @click="showHelp = true" outlined
              >Help</v-btn
            >
          </v-toolbar>
          <!--v-progress-linear v-if="disableForm" indeterminate color="#ffffff"></v-progress-linear-->
          <v-card-text style="padding: 10px">
            <v-select
              :items="defaultParameters.benchmarks"
              item-text="label"
              item-value="value"
              v-model="selectedParameters.benchmark"
              label="Benchmark*"
              outlined
              dense
            ></v-select>
            <v-select
              v-if="selectedParameters.benchmark === 'cosbench'"
              style="margin-top: -15px"
              :items="defaultParameters.operations"
              item-text="label"
              item-value="value"
              v-model="selectedParameters.operation"
              label="Operation*"
              outlined
              dense
            ></v-select>
            <v-select
              v-if="selectedParameters.benchmark === 'fio'"
              style="margin-top: -15px"
              :items="defaultParameters.templates"
              item-text="label"
              item-value="value"
              v-model="selectedParameters.template"
              label="Template*"
              outlined
              dense
            ></v-select>
            <v-select
              style="margin-top: -15px"
              :items="defaultParameters.configurations"
              item-text="label"
              item-value="value"
              v-model="selectedParameters.configuration"
              label="Configuration*"
              outlined
              dense
            ></v-select>
            <v-select
              style="margin-top: -15px"
              v-model="selectedParameters.client"
              :items="defaultParameters.clients"
              item-text="label"
              item-value="value"
              label="Clients*"
              outlined
              dense
              multiple
            ></v-select>
            <v-select
              style="margin-top: -15px"
              v-model="selectedParameters.primary_server"
              :items="defaultParameters.primary_servers"
              item-text="label"
              item-value="value"
              label="Nodes*"
              outlined
              dense
              multiple
            ></v-select>
            <v-text-field
              style="margin-top: -15px"
              type="password"
              label="Password*"
              v-model.trim="selectedParameters.server_password"
              outlined
              dense
            ></v-text-field>
            <v-select
              style="margin-top: -15px"
              :items="defaultParameters.sampling"
              item-text="label"
              item-value="value"
              v-model="selectedParameters.sampling"
              label="Sampling*"
              outlined
              dense
            ></v-select>
            <div>
              <v-btn color="primary" @click="runScript()" v-bind:disabled="btnDisabled">Run Script</v-btn>
              <v-btn
                color="primary"
                @click="clearScriptArgs()"
                style="margin-left: 16px"
                outlined
                >Clear</v-btn
              >
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col col="12" md="9" sm="7">
        <v-card>
          <v-toolbar color="#6ebe49" dense>
            <v-menu offset-y>
              <template v-slot:activator="{ on }">
                <v-btn color="#ffffff" v-on="on" icon>
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item
                  v-for="(scriptExecLog, index) in scriptExecLogs"
                  :key="index"
                  @click="showLog(scriptExecLog)"
                  style="min-width: 150px"
                >
                  <v-list-item-title>{{
                    scriptExecLog.start_time | fromMillis
                  }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <span
              v-if="selectedScriptExecLog"
              style="color: #ffffff; font-size: 18px"
              >{{ selectedScriptExecLog.start_time | fromMillis }}</span
            >
            <span v-else style="color: #ffffff; font-size: 18px">Terminal</span>
          </v-toolbar>
          <v-card-text
            style="
              height: 490px;
              width: 100%;
              background-color: #000000;
              padding: 0px;
            "
          >
            <v-row justify="center">
              <v-col col="12" md="6">
                <div style="border: 1px solid #ffffff; font-size: 13px">
                  <p
                    style="color: #99ff33; margin-bottom: 0; text-align: center"
                  >
                    * Auto-Perf Terminal *
                  </p>
                  <p
                    style="color: #fffc33; margin-bottom: 0; text-align: center"
                  >
                    (View Script execution logs)
                  </p>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col
                class="py-0"
                style="padding-left: 17px; padding-right: 13px"
              >
                <div id="logArea" class="terminal">
                  {{ selectedScriptExecLog ? selectedScriptExecLog.log : "" }}
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-model="showHelp" width="900">
      <v-card>
        <v-card-title
          class="headline"
          style="background-color: #6ebe49; color: #ffffff"
        >
          Help
        </v-card-title>

        <v-card-text style="margin-top: 15px">
          <label
            >Pre-requisite steps to perform AutoPerf s3 performance
            testing:</label
          >
          <ol>
            <li>S3Cluster should be configured with latest build.</li>
            <li>S3Cluster is stable and in running state.</li>
            <li>It must require root access to the S3 client and S3 server.</li>
            <li>
              To enable Passwordless authentication, AutoPerf Dashboard will ask
              you for the password.
            </li>
            <li>
              S3client must be pre-configured. User must be able to perform S3
              bucket Operations. (# aws s3 ls)
            </li>
          </ol>
          <br />
          <label>Note: -</label>
          <ol>
            <li>
              AutoPerf will take care of all configuration like Benchmark tools,
              autoperf and pre-requisites packages on S3 Client and S3 Server.
            </li>
            <li>
              While running fio benchmark, you will observe the S3 performance
              graph (Grafana Dashboard) only on the primary and secondary node
              of S3 Server respectively. It will not be reflected on your Client
              server.
            </li>
            <li>
              For the remaining benchmark, you can observe the s3 performance
              graph (Grafana Dashboard) only on the S3 Client server.
            </li>
          </ol>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showHelp = false"> Ok </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbarConfig.show"
      :color="snackbarConfig.color"
      top
      >{{ snackbarConfig.message }}</v-snackbar
    >
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Api } from "../../services/api";
import apiRegister from "../../services/api-register";

@Component({
  name: "auto-perf-dashboard"
})
export default class AutoPerfDashboard extends Vue {
  public defaultParameters: any = {
    benchmarks: [],
    operations: [],
    templates: [],
    configurations: [],
    clients: [],
    primary_servers: [],
    secondary_servers: [],
    sampling: []
  };

  public selectedParameters: any = {
    benchmark: "",
    operation: "",
    configuration: "",
    client: null,
    primary_server: null,
    secondary_server: null,
    sampling: "",
    client_password: "",
    server_password: ""
  };

  public disableForm: boolean = true;
  public snackbarConfig: any = {
    show: true,
    message: "",
    color: "#6ebe49"
  };

  public isGoToDashboard: boolean = false;
  public showHelp: boolean = false;

  public scriptExecLogs: any[] = [];

  public selectedScriptExecLog: any = null;
  public scriptExecLogPoller: any = null;

  public async mounted() {
    await this.getDefaultParameters();
    await this.getScriptExecLogs();
  }

  public beforeDestroy() {
    this.clearLogPoller();
  }

  public clearLogPoller() {
    if (this.scriptExecLogPoller) {
      clearInterval(this.scriptExecLogPoller);
      this.scriptExecLogPoller = null;
    }
  }

  public async showLog(selectedScriptExecLog: any) {
    this.clearLogPoller();
    if (selectedScriptExecLog.end_time === 0) {
      await this.getScriptExecLogById(selectedScriptExecLog._id);
      this.scriptExecLogPoller = setInterval(async () => {
        await this.getScriptExecLogById(selectedScriptExecLog._id);
        if (this.selectedScriptExecLog.end_time !== 0) {
          this.clearLogPoller();
        }
      }, 5000);
    } else {
      await this.getScriptExecLogById(selectedScriptExecLog._id);
    }
  }

  public async getDefaultParameters() {
    this.showSnackbar("Fetching default parameters...");
    this.disableForm = true;
    const res: any = await Api.getAll(apiRegister.default_parameters);
    if (res && res.data && res.data.result) {
      this.prepareDropdowns(res.data.result);
    }
    this.disableForm = false;
    this.hideSnackbar();
  }

  public async getScriptExecLogs() {
    this.showSnackbar("Fetching last logs...");
    const res: any = await Api.getAll(apiRegister.script_execution, {
      user_gid: localStorage.getItem("gid")
    });
    if (res && res.data && res.data.result) {
      this.scriptExecLogs = res.data.result;
    }
    if (this.scriptExecLogs.length > 0) {
      this.showLog(this.scriptExecLogs[0]);
    }
    this.hideSnackbar();
  }

  public async getScriptExecLogById(scriptExecLogId: string) {
    const res: any = await Api.getAll(
      apiRegister.script_execution + "/" + scriptExecLogId
    );
    if (res && res.data && res.data.result) {
      this.selectedScriptExecLog = res.data.result;
    }
  }

  public async runScript() {
    let res;
    this.showSnackbar("Running script...");
    this.disableForm = true;
    try {
      const scriptArgs: any = {
        benchmark: this.selectedParameters.benchmark,
        configuration: this.selectedParameters.configuration,
        client: this.selectedParameters.client.join(","),
        primary_server: this.selectedParameters.primary_server.join(","),
        sampling: this.selectedParameters.sampling,
        server_password: this.selectedParameters.server_password
      };
      if (scriptArgs.benchmark === "cosbench") {
        scriptArgs.operation = this.selectedParameters.operation;
      }
      if (scriptArgs.benchmark === "fio") {
        scriptArgs.template = this.selectedParameters.template;
      }
      res = await Api.post(apiRegister.script_execution, {
        script_name: "s3workloads",
        script_args: scriptArgs
      });
    } catch (err) {
      res = err;
    }
    this.disableForm = false;
    this.hideSnackbar();
    if (res.status === 200) {
      this.showSnackbar(res.data.message);
      this.isGoToDashboard = true;
      this.getScriptExecLogs();
    } else {
      this.showSnackbar(res.data.message, false);
    }
  }

  public clearScriptArgs() {
    this.selectedParameters.benchmark = "";
    this.selectedParameters.operation = "";
    this.selectedParameters.configuration = "";
    this.selectedParameters.client = null;
    this.selectedParameters.primary_server = null;
    this.selectedParameters.secondary_server = null;
    this.selectedParameters.sampling = "";
    this.selectedParameters.client_password = "";
    this.selectedParameters.server_password = "";
  }

  get btnDisabled() {
    let isValidBenchmark = false;
    if (this.selectedParameters.benchmark) {
      isValidBenchmark = true;
      if (this.selectedParameters.benchmark === "cosbench") {
        if (!this.selectedParameters.operation) {
          isValidBenchmark = false;
        }
      }
      if (this.selectedParameters.benchmark === "fio") {
        if (!this.selectedParameters.template) {
          isValidBenchmark = false;
        }
      }
    }

    return !(
      isValidBenchmark &&
      this.selectedParameters.configuration &&
      this.selectedParameters.client &&
      this.selectedParameters.primary_server &&
      this.selectedParameters.sampling
    );
  }

  get graphanaURL() {
    return (
      "http://" +
      location.hostname +
      ":3000/d/1U980bWGk/cortx-autoperf?orgId=1&refresh=5s&var-int=eno1&var-path=%2F&var-server=" +
      this.selectedParameters.client
    );
  }

  private showSnackbar(message: string, isSuccess: boolean = true) {
    this.snackbarConfig.show = true;
    this.snackbarConfig.message = message;
    this.snackbarConfig.color = isSuccess ? "#6ebe49" : "#dc1f2e";
  }

  private hideSnackbar() {
    this.snackbarConfig.show = false;
    this.snackbarConfig.message = "";
  }

  private prepareDropdowns(defaultParameters: any) {
    defaultParameters.benchmarks.forEach((benchmark: string) => {
      this.defaultParameters.benchmarks.push({
        label: benchmark,
        value: benchmark
      });
    });
    defaultParameters.operations.forEach((operation: string) => {
      this.defaultParameters.operations.push({
        label: operation,
        value: operation
      });
    });
    defaultParameters.templates.forEach((template: string) => {
      this.defaultParameters.templates.push({
        label: template,
        value: template
      });
    });
    defaultParameters.configurations.forEach((configuration: string) => {
      this.defaultParameters.configurations.push({
        label: configuration,
        value: configuration
      });
    });
    defaultParameters.clients.forEach((client: string) => {
      this.defaultParameters.clients.push({
        label: client,
        value: client
      });
    });
    defaultParameters.primary_servers.forEach((server: string) => {
      this.defaultParameters.primary_servers.push({
        label: server,
        value: server
      });
    });
    defaultParameters.secondary_servers.forEach((server: string) => {
      this.defaultParameters.secondary_servers.push({
        label: server,
        value: server
      });
    });
    defaultParameters.sampling.forEach((samplingItem: string) => {
      this.defaultParameters.sampling.push({
        label: samplingItem,
        value: samplingItem
      });
    });
  }
}
</script>
<style lang="scss" scoped>
.dashboard-padding {
  padding-left: 10px;
  padding-right: 10px;
}
.terminal {
  color: #ffffff;
  font-size: 15px;
  width: 100%;
  height: 415px;
  overflow-y: scroll;
  white-space: pre-wrap;
}
.card-title {
  background-color: #6ebe49;
  color: #ffffff;
  padding: 3px 15px 3px 15px;
  font-size: 18px;
}
</style>
