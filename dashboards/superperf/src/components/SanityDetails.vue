<template>
  <v-container>
    <v-card v-if="headers && headers.length > 0">
      <SanityDataTable
        TableName="Throughput (MBps)"
        v-if="dataThroughputWrite && dataThroughputWrite.length > 0"
        :Headers="headers"
        :DataValuesRead="dataThroughputRead"
        :DataValuesWrite="dataThroughputWrite"
      />
      <SanityDataTable
        TableName="Latency (ms)"
        :Headers="headers"
        :DataValuesRead="dataLatencyRead"
        :DataValuesWrite="dataLatencyWrite"
      />
      <SanityDataTable
        TableName="IOPS"
        :Headers="headers"
        :DataValuesRead="dataIopsRead"
        :DataValuesWrite="dataIopsWrite"
      />
      <SanityDataTable
        TableName="TTFB (ms)"
        :Headers="headers"
        :DataValuesRead="dataTtfbRead"
        :DataValuesWrite="dataTtfbWrite"
      />
    </v-card>
  </v-container>
</template>

<script>
import SanityDataTable from "./SanityDataTable.vue";
import * as sanityapi from "./backend/getSanityData.js";

export default {
  name: "SanityDetailsPage",
  components: {
    SanityDataTable,
  },
  data() {
    return {
      run_id: this.$route.query.run_id,
      queryResultsTput: [],
      queryResultsLat: [],
      queryResultsIops: [],
      queryResultsTtfb: [],
      headers: [],
      dataThroughputRead: [],
      dataThroughputWrite: [],
      dataLatencyRead: [],
      dataLatencyWrite: [],
      dataIopsRead: [],
      dataIopsWrite: [],
      dataTtfbRead: [],
      dataTtfbWrite: [],
    };
  },
  mounted: function () {
    sanityapi
      .fetchDataFromResponse(this.run_id, "throughput")
      .then((response) => {
        this.queryResultsTput = response.data.result;
        this.headers = sanityapi.getHeaderOfSanity(this.queryResultsTput, "baseline");
        this.dataThroughputRead = sanityapi.getDataForSanityTables(
          this.queryResultsTput["read"]
        );
        this.dataThroughputWrite = sanityapi.getDataForSanityTables(
          this.queryResultsTput["write"]
        );
      });

    sanityapi
      .fetchDataFromResponse(this.run_id, "latency")
      .then((response) => {
        this.queryResultsLat = response.data.result;
        this.dataLatencyRead = sanityapi.getDataForSanityTables(
          this.queryResultsLat["read"]
        );
        this.dataLatencyWrite = sanityapi.getDataForSanityTables(
          this.queryResultsLat["write"]
        );
      });

    sanityapi.fetchDataFromResponse(this.run_id, "iops").then((response) => {
      this.queryResultsIops = response.data.result;
      this.dataIopsRead = sanityapi.getDataForSanityTables(
        this.queryResultsIops["read"]
      );
      this.dataIopsWrite = sanityapi.getDataForSanityTables(
        this.queryResultsIops["write"]
      );
    });

    sanityapi.fetchDataFromResponse(this.run_id, "ttfb").then((response) => {
      this.queryResultsTtfb = response.data.result;
      this.dataTtfbRead = sanityapi.getDataForSanityTables(
        this.queryResultsTtfb["read"]
      );
      this.dataTtfbWrite = sanityapi.getDataForSanityTables(
        this.queryResultsTtfb["write"]
      );
    });
  },
};
</script>