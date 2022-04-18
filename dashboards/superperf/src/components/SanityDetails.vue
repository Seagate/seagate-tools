<template>
  <v-container>
    <v-card v-if="headers && headers.length > 0">
      <SanityDataTable
        TableName="Throughput (MBps)"
        v-if="data_throughput_write && data_throughput_write.length > 0"
        :Headers="headers"
        :DataValuesRead="data_throughput_read"
        :DataValuesWrite="data_throughput_write"
      />
      <SanityDataTable
        TableName="Latency (ms)"
        :Headers="headers"
        :DataValuesRead="data_latency_read"
        :DataValuesWrite="data_latency_write"
      />
      <SanityDataTable
        TableName="IOPS"
        :Headers="headers"
        :DataValuesRead="data_iops_read"
        :DataValuesWrite="data_iops_write"
      />
      <SanityDataTable
        TableName="TTFB (ms)"
        :Headers="headers"
        :DataValuesRead="data_ttfb_read"
        :DataValuesWrite="data_ttfb_write"
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
  data: () => ({
    run_id: null,
    query_results_tput: [],
    query_results_lat: [],
    query_results_iops: [],
    query_results_ttfb: [],
    headers: [],
    data_throughput_read: [],
    data_throughput_write: [],
    data_latency_read: [],
    data_latency_write: [],
    data_iops_read: [],
    data_iops_write: [],
    data_ttfb_read: [],
    data_ttfb_write: [],
  }),
  mounted: function () {
    this.run_id = this.$route.query.run_id;
    console.log(this.$route.query.id);
    sanityapi
      .fetch_data_from_respose(this.run_id, "throughput")
      .then((response) => {
        this.query_results_tput = response.data.result;
        this.headers = sanityapi.get_header_of_sanity(this.query_results_tput);
        this.data_throughput_read = sanityapi.get_data_for_sanity_tables(
          this.query_results_tput["read"]
        );
        console.log(this.data_throughput_read);
        this.data_throughput_write = sanityapi.get_data_for_sanity_tables(
          this.query_results_tput["write"]
        );
      });

    sanityapi
      .fetch_data_from_respose(this.run_id, "latency")
      .then((response) => {
        this.query_results_lat = response.data.result;
        this.data_latency_read = sanityapi.get_data_for_sanity_tables(
          this.query_results_lat["read"]
        );
        this.data_latency_write = sanityapi.get_data_for_sanity_tables(
          this.query_results_lat["write"]
        );
      });

    sanityapi.fetch_data_from_respose(this.run_id, "iops").then((response) => {
      this.query_results_iops = response.data.result;
      this.data_iops_read = sanityapi.get_data_for_sanity_tables(
        this.query_results_iops["read"]
      );
      this.data_iops_write = sanityapi.get_data_for_sanity_tables(
        this.query_results_iops["write"]
      );
    });

    sanityapi.fetch_data_from_respose(this.run_id, "ttfb").then((response) => {
      this.query_results_ttfb = response.data.result;
      this.data_ttfb_read = sanityapi.get_data_for_sanity_tables(
        this.query_results_ttfb["read"]
      );
      this.data_ttfb_write = sanityapi.get_data_for_sanity_tables(
        this.query_results_ttfb["write"]
      );
    });
  },
};
</script>