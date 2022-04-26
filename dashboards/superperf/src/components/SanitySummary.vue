<template>
  <v-expansion-panels focusable  class="sanity_summary">
    <v-expansion-panel>
      <v-expansion-panel-header>Sanity Run Summary</v-expansion-panel-header>
      <v-expansion-panel-content>
       <div>
           <h4>Run ID: {{ run_id }}</h4>
           <h4 style='display:inline'>User: </h4> <p style='display:inline'>{{ configData['User'] }}</p>
           <div>
           <h4 style='display:inline'>Nodes ({{ configData['Count_of_Servers'] }}): </h4>
           <p style='display:inline'>{{ configData['Nodes'].join([separator = ', ']) }}</p>
           </div>
           <div>
            <h4 style='display:inline'>Clients ({{ configData['Count_of_Clients'] }}): </h4>
            <p style='display:inline'>{{ configData['Clients'].join([separator = ', ']) }}</p>
           </div>
           <div>
             <h4 style='display:inline'>Cluster Fill: </h4>
             <p style='display:inline'>{{ configData['Percentage_full'] }}%</p>
           </div>
       </div>

       <v-card v-if="headers && headers.length > 0">
        <SanityDataTable
          TableName="Data"
          v-if="data_summary_read && data_summary_read.length>0"
          :Headers="headers"
          :DataValuesRead="data_summary_read"
          :DataValuesWrite="data_summary_write"
        />
      </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
import * as sanityapi from "./backend/getSanityData.js";
import SanityDataTable from "./SanityDataTable.vue";

export default {
    name: "SanitySummary",
    components: {
    SanityDataTable,
    },
    data() {
        return {
          configData: {
          },
          run_id: this.$route.query.run_id,
          headers: [],
          data_summary_tput: [],
          data_summary_read: [],
          data_summary_write: [],
        };
    },
    mounted: function() {
      sanityapi.fetchDataFromResponse(this.run_id, "config")
        .then((response) => {
          this.configData = response.data;
      });

      sanityapi
      .fetchDataFromResponse(this.run_id, "others")
      .then((response) => {
        this.data_summary_tput = response.data.result;
        this.headers = sanityapi.getHeaderOfSanity(this.data_summary_tput, "objects");
        this.data_summary_read = sanityapi.getDataForSanityTables(
          this.data_summary_tput["read"]
        );
        this.data_summary_write = sanityapi.getDataForSanityTables(
          this.data_summary_tput["write"]
        );
      });

    }
  };
</script>

<style>
 .sanity_summary {
   padding-left: 20px;
   padding-right: 20px;

 }
</style>