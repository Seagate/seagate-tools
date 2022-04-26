<template>
  <v-expansion-panels focusable  class="sanity_summary">
    <v-expansion-panel>
      <v-expansion-panel-header>Sanity Run Summary</v-expansion-panel-header>
      <v-expansion-panel-content>
       <div>
           <h4>Run ID: {{ run_id }}</h4>
           <h4 style='display:inline'>User: </h4> <p style='display:inline'>{{ config_data['User'] }}</p>
           <div>
           <h4 style='display:inline'>Nodes ({{ config_data['Count_of_Servers'] }}): </h4>
           <p style='display:inline'>{{ config_data['Nodes'].join([separator = ', ']) }}</p>
           </div>
           <div>
            <h4 style='display:inline'>Clients ({{ config_data['Count_of_Clients'] }}): </h4>
            <p style='display:inline'>{{ config_data['Clients'].join([separator = ', ']) }}</p>
           </div>
           <div>
             <h4 style='display:inline'>Cluster Fill: </h4>
             <p style='display:inline'>{{ config_data['Percentage_full'] }}%</p>
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
          config_data: {
          },
          run_id: this.$route.query.run_id,
          headers: [],
          data_summary_tput: [],
          data_summary_read: [],
          data_summary_write: [],
        };
    },
    mounted: function() {
      sanityapi.fetch_data_from_respose(this.run_id, "config")
        .then((response) => {
          this.config_data = response.data;
      });

      sanityapi
      .fetch_data_from_respose(this.run_id, "others")
      .then((response) => {
        this.data_summary_tput = response.data.result;
        this.headers = sanityapi.get_header_of_sanity(this.data_summary_tput, "objects");
        this.data_summary_read = sanityapi.get_data_for_sanity_tables(
          this.data_summary_tput["read"]
        );
        this.data_summary_write = sanityapi.get_data_for_sanity_tables(
          this.data_summary_tput["write"]
        );
      });

    },
  }
</script>

<style>
 .sanity_summary {
   padding-left: 20px;
   padding-right: 20px;

 }
</style>