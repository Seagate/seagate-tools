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
          v-if="dataSummaryRead && dataSummaryRead.length>0"
          :Headers="headers"
          :DataValuesRead="dataSummaryRead"
          :DataValuesWrite="dataSummaryWrite"
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
          dataSummaryTput: [],
          dataSummaryRead: [],
          dataSummaryWrite: [],
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
        this.dataSummaryTput = response.data.result;
        this.headers = sanityapi.getHeaderOfSanity(this.dataSummaryTput, "objects");
        this.dataSummaryRead = sanityapi.getDataForSanityTables(
          this.dataSummaryTput["read"]
        );
        this.dataSummaryWrite = sanityapi.getDataForSanityTables(
          this.dataSummaryTput["write"]
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