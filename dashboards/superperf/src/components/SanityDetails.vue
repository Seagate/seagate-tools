<!--
*  Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
*
*  This program is free software: you can redistribute it and/or modify
*  it under the terms of the GNU Affero General Public License as published
*  by the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*  GNU Affero General Public License for more details.
*  You should have received a copy of the GNU Affero General Public License
*  along with this program. If not, see <https:  www.gnu.org/licenses/>.
*
*  For any questions about this software or licensing,
*  please email opensource@seagate.com or cortx-questions@seagate.com.
*
*  -*- coding: utf-8 -*-
-->
// Seagate-tools: Sanity Page layout for a Performance run

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
      <SanityAllMatrixTable
        TableName="Max Concurrency"
        :Headers="allHeaders"
        :DataValues="dataAll"
      />
    </v-card>
  </v-container>
</template>

<script>
import SanityDataTable from "./SanityDataTable.vue";
import SanityAllMatrixTable from "./SanityAllMatrixTable.vue";
import * as sanityapi from "./backend/getSanityData.js";

export default {
  name: "SanityDetailsPage",
  components: {
    SanityDataTable,
    SanityAllMatrixTable,
  },
  data() {
    return {
      run_id: this.$route.query.run_id,
      headers: [],
      allHeaders: [],
      dataThroughputRead: [],
      dataThroughputWrite: [],
      dataLatencyRead: [],
      dataLatencyWrite: [],
      dataIopsRead: [],
      dataIopsWrite: [],
      dataTtfbRead: [],
      dataTtfbWrite: [],
      dataAll: [],
    };
  },
  mounted() {
    sanityapi
      .fetchDataFromResponse(this.run_id, "throughput")
      .then((response) => {
        let queryResultsTput = response.data.result;
        this.headers = sanityapi.getHeaderOfSanityfromBaseline(
          queryResultsTput,
        );
        this.dataThroughputRead = sanityapi.getDataForSanityTables(
          queryResultsTput.read
        );
        this.dataThroughputWrite = sanityapi.getDataForSanityTables(
          queryResultsTput.write
        );
      });

    sanityapi.fetchDataFromResponse(this.run_id, "latency").then((response) => {
      let queryResultsLat = response.data.result;
      this.dataLatencyRead = sanityapi.getDataForSanityTables(
        queryResultsLat.read
      );
      this.dataLatencyWrite = sanityapi.getDataForSanityTables(
        queryResultsLat.write
      );
    });

    sanityapi.fetchDataFromResponse(this.run_id, "iops").then((response) => {
      let queryResultsIops = response.data.result;
      this.dataIopsRead = sanityapi.getDataForSanityTables(
        queryResultsIops.read
      );
      this.dataIopsWrite = sanityapi.getDataForSanityTables(
        queryResultsIops.write
      );
    });

    sanityapi.fetchDataFromResponse(this.run_id, "ttfb").then((response) => {
      let queryResultsTtfb = response.data.result;
      this.dataTtfbRead = sanityapi.getDataForSanityTables(
        queryResultsTtfb.read
      );
      this.dataTtfbWrite = sanityapi.getDataForSanityTables(
        queryResultsTtfb.write
      );
    });

    sanityapi.fetchDataFromResponse(this.run_id, "all").then((response) => {
      let dataAllMetrix = response.data.result;
      this.allHeaders = sanityapi.getHeaderOfSanityforMaxSessions(dataAllMetrix);
      this.dataAll = sanityapi.getDataForSanityTables(dataAllMetrix);
    });
  },
};
</script>