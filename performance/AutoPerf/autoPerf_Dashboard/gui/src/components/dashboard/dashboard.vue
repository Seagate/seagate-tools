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
            >Grafana</v-btn>
            <v-btn small color="#ffffff" @click="showHelp = true" outlined>Help</v-btn>
          </v-toolbar>
          <!--v-progress-linear v-if="disableForm" indeterminate color="#ffffff"></v-progress-linear-->
          <v-card-text style="padding: 10px">
            <v-select
              style="margin-top: 5px"
              v-model="selectedParameters.primary_server"
              :items="defaultParameters.primary_servers"
              item-text="label"
              item-value="value"
              label="Nodes*"
              outlined
              dense
              multiple
            ></v-select>
            <v-btn
              color="primary"
              x-small
              text
              style="margin-top: -50px;"
              @click="addNodeDialog = true"
            >Add Node</v-btn>
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
            <v-btn
              color="primary"
              x-small
              text
              style="margin-top: -50px;"
              @click="addClientDialog = true"
            >Add Client</v-btn>
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
            <div style="margin-top: -15px">
              <label for>Select Benchmark</label>
              <v-radio-group
                style="margin-top: 1px"
                v-model="isBenchmarkSelected"
                row
                @change="resetIsBenchmarkSelected"
              >
                <v-radio label="Yes" value="yes"></v-radio>
                <v-radio label="No" value="no"></v-radio>
              </v-radio-group>
            </div>
            <div v-if="isBenchmarkSelected === 'yes'">
              <v-select
                :items="defaultParameters.benchmarks"
                item-text="label"
                item-value="value"
                v-model="selectedParameters.benchmark"
                label="Benchmark*"
                outlined
                dense
                style="margin-top: -8px"
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
              <v-btn
                color="primary"
                x-small
                text
                style="margin-top: -50px;"
                @click="configHelpTextDialog = true"
              >Help*</v-btn>

              <!-- Add Start -->
              <div
                v-if="selectedParameters.benchmark === 's3bench_basic' && selectedParameters.configuration === 'custom'"
              >
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.clientCoun"
                  label="Client Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectsCount"
                  label="Objects Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectSize"
                  label="Object Size"
                  type="number"
                ></v-text-field>
                <div style="margin-top: -40px" v-if="selectedParameters.objectSize">
                  <v-radio-group v-model="isObjectSizeSelected" row>
                    <v-radio label="KB" value="KB"></v-radio>
                    <v-radio label="MB" value="MB"></v-radio>
                    <v-radio label="GB" value="GB"></v-radio>
                  </v-radio-group>
                </div>
                <v-text-field
                  style="margin-top: -5px"
                  outlined
                  dense
                  v-model="selectedParameters.graphSamplingRate"
                  label="Graph Sampling Rate"
                  type="number"
                ></v-text-field>
              </div>

              <div
                v-if="selectedParameters.benchmark === 'hsbench' && selectedParameters.configuration === 'custom'"
              >
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.bucketsCount"
                  label="Buckets Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectsCount"
                  label="Objects Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectSize"
                  label="Object Size"
                  type="number"
                ></v-text-field>
                <div style="margin-top: -40px" v-if="selectedParameters.objectSize">
                  <v-radio-group v-model="isObjectSizeSelected" row>
                    <v-radio label="KB" value="KB"></v-radio>
                    <v-radio label="MB" value="MB"></v-radio>
                    <v-radio label="GB" value="GB"></v-radio>
                  </v-radio-group>
                </div>
                <v-text-field
                  style="margin-top: -5px"
                  outlined
                  dense
                  v-model="selectedParameters.clientCoun"
                  label="Client Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.testDuration"
                  label="Test Duration"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.graphSamplingRate"
                  label="Graph Sampling Rate"
                  type="number"
                ></v-text-field>
              </div>

              <div
                v-if="selectedParameters.benchmark === 'cosbench' && selectedParameters.configuration === 'custom'"
              >
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.clientCoun"
                  label="Client Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectsCount"
                  label="Objects Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.objectSize"
                  label="Object Size"
                  type="number"
                ></v-text-field>
                <div style="margin-top: -40px" v-if="selectedParameters.objectSize">
                  <v-radio-group v-model="isObjectSizeSelected" row>
                    <v-radio label="KB" value="KB"></v-radio>
                    <v-radio label="MB" value="MB"></v-radio>
                    <v-radio label="GB" value="GB"></v-radio>
                  </v-radio-group>
                </div>
                <v-text-field
                  style="margin-top: -5px"
                  outlined
                  dense
                  v-model="selectedParameters.bucketsCount"
                  label="Buckets Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.testDuration"
                  label="Test Duration"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.graphSamplingRate"
                  label="Graph Sampling Rate"
                  type="number"
                ></v-text-field>
              </div>

              <div
                v-if="selectedParameters.benchmark === 'fio' && selectedParameters.configuration === 'custom'"
              >
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.testDuration"
                  label="Test Duration"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.blockSize"
                  label="Block Size"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.jobsCount"
                  label="Jobs Count"
                  type="number"
                ></v-text-field>
                <v-text-field
                  style="margin-top: -15px"
                  outlined
                  dense
                  v-model="selectedParameters.samples"
                  label="Samples"
                  type="number"
                ></v-text-field>
              </div>
            </div>
            <div v-if="isBenchmarkSelected === 'no'">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    style="margin-top: -20px"
                    label="Time Scale"
                    type="number"
                    min="1"
                    max="60"
                    hint="Number should be 1 to 60"
                    :rules="[
                      () => !!selectedParameters.time_scale || 'This field is required',
                      () => !!selectedParameters.time_scale && selectedParameters.time_scale <= 60 || 'Time scale must be less than 60',
                    ]"
                    required
                    outlined
                    dense
                    v-model="selectedParameters.time_scale"
                  ></v-text-field>
                </v-col>
              </v-row>
            </div>

            <div>
              <v-btn
                color="primary"
                @click="runScript()"
                v-bind:disabled="btnDisabled"
              >{{ isBenchmarkSelected == 'yes' ? 'RUN SCRIPT' : 'START MONITORING' }}</v-btn>
              <v-btn
                color="primary"
                @click="clearScriptArgs()"
                style="margin-left: 16px"
                outlined
              >Clear</v-btn>
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
                  <v-list-item-title>
                    {{
                    scriptExecLog.start_time | fromMillis
                    }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <span
              v-if="selectedScriptExecLog"
              style="color: #ffffff; font-size: 18px"
            >{{ selectedScriptExecLog.start_time | fromMillis }}</span>
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
                  >* Auto-Perf Terminal *</p>
                  <p
                    style="color: #fffc33; margin-bottom: 0; text-align: center"
                  >(View Script execution logs)</p>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0" style="padding-left: 17px; padding-right: 13px">
                <div
                  id="logArea"
                  class="terminal"
                >{{ selectedScriptExecLog ? selectedScriptExecLog.log : "" }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-model="showHelp" width="900">
      <v-card>
        <v-card-title class="headline" style="background-color: #6ebe49; color: #ffffff">Help</v-card-title>

        <v-card-text style="margin-top: 15px">
          <label>
            Pre-requisite steps to perform AutoPerf s3 performance
            testing:
          </label>
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
              of S3 Server respectively. It will not be reflected on your Client
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
          <v-btn color="primary" @click="showHelp = false">Ok</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="addNodeDialog" width="500" persistent>
      <v-card>
        <v-card-title class="headline" style="background-color: #6ebe49; color: #ffffff">Add Node</v-card-title>

        <v-card-text>
          <v-text-field
            class="mt-5"
            label="Node*"
            v-model.trim="addMetadataForm.node"
            outlined
            dense
          ></v-text-field>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="addNode()" :disabled="!addMetadataForm.node">Add</v-btn>
          <v-btn color="primary" @click="cancelAddNode()" class="ml-4 mr-2" outlined>Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="addClientDialog" width="500" persistent>
      <v-card>
        <v-card-title class="headline" style="background-color: #6ebe49; color: #ffffff">Add Client</v-card-title>

        <v-card-text>
          <v-text-field
            class="mt-5"
            label="Client*"
            v-model.trim="addMetadataForm.client"
            outlined
            dense
          ></v-text-field>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="addClient()" :disabled="!addMetadataForm.client">Add</v-btn>
          <v-btn color="primary" @click="cancelAddClient()" class="ml-4 mr-2" outlined>Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="configHelpTextDialog" width="650" persistent>
      <v-card>
        <v-card-title
          class="headline"
          style="background-color: #6ebe49; color: #ffffff"
        >Configuration</v-card-title>

        <div>
          <v-data-table
            :headers="headers"
            :items="desserts"
            hide-default-footer
            class="elevation-1"
          >
            <template v-slot:header.name="{ header }">{{ header.text.toUpperCase() }}</template>
          </v-data-table>
        </div>
        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <!-- <v-btn color="primary" @click="addNode()" :disabled="!addMetadataForm.node">Add</v-btn> -->
          <v-btn color="primary" @click="cancleConfigHelpTextDialog()" class="ml-4 mr-2" outlined>Ok</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbarConfig.show"
      :color="snackbarConfig.color"
      top
    >{{ snackbarConfig.message }}</v-snackbar>
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
  public isBenchmarkSelected: string = "yes"; // Select Benchmark Option "yes or no"
  public isObjectSizeSelected: string = "KB"; // Select Object size Option "KB or MB or GB"

  public resetIsBenchmarkSelected() {
    if (this.isBenchmarkSelected == "yes") {
      this.selectedParameters.time_scale = null;
    } else {
      this.selectedParameters.benchmark = "";
      this.selectedParameters.configuration = "";
      this.selectedParameters.operation = "";
      this.selectedParameters.clientCoun = null;
      this.selectedParameters.objectsCount = null;
      this.selectedParameters.objectSize = null;
      this.selectedParameters.bucketsCount = null;
      this.selectedParameters.testDuration = null;
      this.selectedParameters.graphSamplingRate = null;
      this.selectedParameters.blockSize = null;
      this.selectedParameters.jobsCount = null;
      this.selectedParameters.samples = null;
    }
  }

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
    server_password: "",
    time_scale: null,
    clientCoun: null,
    objectsCount: null,
    objectSize: null,
    bucketsCount: null,
    testDuration: null,
    graphSamplingRate: null,
    blockSize: null,
    jobsCount: null,
    samples: null
  };

  public headers: any[] = [
    { text: "", value: "name" },
    { text: "BUCKETS", value: "buckets" },
    { text: "CLIENTS", value: "clients" },
    { text: "NUMJOBS", value: "numjobs" },
    { text: "NUMSAMPLES", value: "numsamples" },
    { text: "IOSIZE", value: "iosize" },
    { text: "DURATION", value: "duration" },
  ];

  public desserts: any[] = [
    {
      name: "SHORT",
      buckets: "4",
      clients: "32",
      numjobs: "16",
      numsamples: "2048, 4096",
      iosize: "1Mb, 4Mb, 8Mb",
      duration: "300"
    },
    {
      name: "LONG",
      buckets: "8",
      clients: "64",
      numjobs: "32",
      numsamples: "2048, 4096",
      iosize: "32Mb, 64Mb",
      duration: "600"
    },
    {
      name: "SMALL",
      buckets: "16",
      clients: "128, 256",
      numjobs: "16",
      numsamples: "4096",
      iosize: "4Mb, 16Mb, 32Mb",
      duration: "300"
    },
    {
      name: "LARGE",
      buckets: "32",
      clients: "128, 256",
      numjobs: "16",
      numsamples: "4096",
      iosize: "64Mb, 128Mb, 256Mb",
      duration: "600"
    }
  ];
  public disableForm: boolean = true;
  public snackbarConfig: any = {
    show: true,
    message: "",
    color: "#6ebe49"
  };

  public isGoToDashboard: boolean = false;
  public showHelp: boolean = false;
  public addNodeDialog: boolean = false;
  public configHelpTextDialog: boolean = false;
  public addClientDialog: boolean = false;

  public addMetadataForm: any = {
    node: "",
    client: ""
  };

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
        client: this.selectedParameters.client.join(","),
        primary_server: this.selectedParameters.primary_server.join(","),
        sampling: this.selectedParameters.sampling,
        server_password: this.selectedParameters.server_password
      };
      if (this.isBenchmarkSelected === "yes") {
        scriptArgs["is_benchmark_selected"] = true;
        scriptArgs["benchmark"] = this.selectedParameters.benchmark;
        scriptArgs["configuration"] = this.selectedParameters.configuration;
        if (
          scriptArgs.benchmark === "s3bench_basic" &&
          scriptArgs.configuration === "custom"
        ) {
          scriptArgs.clientCoun = this.selectedParameters.clientCoun;
          scriptArgs.objectsCount = this.selectedParameters.objectsCount;
          scriptArgs.objectSize =
            this.selectedParameters.objectSize + this.isObjectSizeSelected;
          scriptArgs.graphSamplingRate = this.selectedParameters.graphSamplingRate;
        }
        if (
          scriptArgs.benchmark === "hsbench" &&
          scriptArgs.configuration === "custom"
        ) {
          scriptArgs.bucketsCount = this.selectedParameters.bucketsCount;
          scriptArgs.objectsCount = this.selectedParameters.objectsCount;
          scriptArgs.objectSize =
            this.selectedParameters.objectSize + this.isObjectSizeSelected;
          scriptArgs.clientCoun = this.selectedParameters.clientCoun;
          scriptArgs.testDuration = this.selectedParameters.testDuration;
          scriptArgs.graphSamplingRate = this.selectedParameters.graphSamplingRate;
        }
        if (
          scriptArgs.benchmark === "cosbench" &&
          scriptArgs.configuration === "custom"
        ) {
          scriptArgs.clientCoun = this.selectedParameters.clientCoun;
          scriptArgs.objectsCount = this.selectedParameters.objectsCount;
          scriptArgs.objectSize =
            this.selectedParameters.objectSize + this.isObjectSizeSelected;
          scriptArgs.bucketsCount = this.selectedParameters.bucketsCount;
          scriptArgs.testDuration = this.selectedParameters.testDuration;
          scriptArgs.graphSamplingRate = this.selectedParameters.graphSamplingRate;
        }
        if (
          scriptArgs.benchmark === "fio" &&
          scriptArgs.configuration === "custom"
        ) {
          scriptArgs.testDuration = this.selectedParameters.testDuration;
          scriptArgs.blockSize = this.selectedParameters.blockSize;
          scriptArgs.jobsCount = this.selectedParameters.jobsCount;
          scriptArgs.samples = this.selectedParameters.samples;
        }
        if (scriptArgs.benchmark === "cosbench") {
          scriptArgs.operation = this.selectedParameters.operation;
        }
        if (scriptArgs.benchmark === "fio") {
          scriptArgs.template = this.selectedParameters.template;
        }
      } else {
        scriptArgs["is_benchmark_selected"] = false;
        scriptArgs["time_scale"] = this.selectedParameters.time_scale;
      }

      res = await Api.post(apiRegister.script_execution, {
        script_name: "s3workloads",
        script_args: scriptArgs
      });
      // console.log("Passing final scriptArgs", scriptArgs);
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
    this.selectedParameters.time_scale = null;
    this.selectedParameters.clientCoun = null;
    this.selectedParameters.objectsCount = null;
    this.selectedParameters.objectSize = null;
    this.selectedParameters.bucketsCount = null;
    this.selectedParameters.testDuration = null;
    this.selectedParameters.graphSamplingRate = null;
    this.selectedParameters.blockSize = null;
    this.selectedParameters.jobsCount = null;
    this.selectedParameters.samples = null;
  }

  get btnDisabled() {
    let isValidBenchmark = false;
    if (this.isBenchmarkSelected === "yes") {
      if (this.selectedParameters.benchmark) {
        isValidBenchmark = true;
        if (
          this.selectedParameters.benchmark === "s3bench_basic" &&
          this.selectedParameters.configuration === "custom"
        ) {
          if (!this.selectedParameters.clientCoun) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectsCount) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectSize) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.graphSamplingRate) {
            isValidBenchmark = false;
          }
        }

        if (
          this.selectedParameters.benchmark === "hsbench" &&
          this.selectedParameters.configuration === "custom"
        ) {
          if (!this.selectedParameters.bucketsCount) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectsCount) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectSize) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.clientCoun) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.testDuration) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.graphSamplingRate) {
            isValidBenchmark = false;
          }
        }
        if (this.selectedParameters.benchmark === "cosbench") {
          if (!this.selectedParameters.operation) {
            isValidBenchmark = false;
          }
        }
        if (
          this.selectedParameters.benchmark === "cosbench" &&
          this.selectedParameters.configuration === "custom"
        ) {
          if (!this.selectedParameters.clientCoun) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectsCount) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.objectSize) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.bucketsCount) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.testDuration) {
            isValidBenchmark = false;
          }
          if (!this.selectedParameters.graphSamplingRate) {
            isValidBenchmark = false;
          }
        }
        if (this.selectedParameters.benchmark === "fio") {
          if (!this.selectedParameters.template) {
            isValidBenchmark = false;
          }
          if (
            this.selectedParameters.benchmark === "fio" &&
            this.selectedParameters.configuration === "custom"
          ) {
            if (!this.selectedParameters.testDuration) {
              isValidBenchmark = false;
            }
            if (!this.selectedParameters.blockSize) {
              isValidBenchmark = false;
            }
            if (!this.selectedParameters.jobsCount) {
              isValidBenchmark = false;
            }
            if (!this.selectedParameters.samples) {
              isValidBenchmark = false;
            }
          }
        }
      }
    } else {
      if (this.selectedParameters.time_scale) {
        isValidBenchmark = true;
      }
    }

    return !(
      (isValidBenchmark &&
        this.selectedParameters.configuration &&
        this.selectedParameters.client &&
        this.selectedParameters.primary_server &&
        this.selectedParameters.sampling) ||
      this.selectedParameters.time_scale
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

  public async addNode() {
    this.addNodeDialog = false;
    this.showSnackbar("Adding Node...");
    const res: any = await Api.post(apiRegister.metadata_node, {
      node: this.addMetadataForm.node
    });
    this.addMetadataForm.node = "";
    if (res && res.data) {
      this.hideSnackbar();
      await this.getDefaultParameters();
    } else {
      this.hideSnackbar();
    }
  }

  public cancelAddNode() {
    this.addMetadataForm.node = "";
    this.addNodeDialog = false;
  }
  public cancleConfigHelpTextDialog() {
    this.configHelpTextDialog = false;
  }
  public async addClient() {
    this.addClientDialog = false;
    this.showSnackbar("Adding Client...");
    const res: any = await Api.post(apiRegister.metadata_client, {
      client: this.addMetadataForm.client
    });
    this.addMetadataForm.client = "";
    if (res && res.data) {
      this.hideSnackbar();
      await this.getDefaultParameters();
    } else {
      this.hideSnackbar();
    }
  }

  public cancelAddClient() {
    this.addMetadataForm.client = "";
    this.addClientDialog = false;
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
    this.clearDropdowns();
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

  private clearDropdowns() {
    this.defaultParameters.benchmarks = [];
    this.defaultParameters.operations = [];
    this.defaultParameters.templates = [];
    this.defaultParameters.configurations = [];
    this.defaultParameters.clients = [];
    this.defaultParameters.primary_servers = [];
    this.defaultParameters.secondary_servers = [];
    this.defaultParameters.sampling = [];
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