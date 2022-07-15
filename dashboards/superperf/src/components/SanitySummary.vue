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
// Seagate-tools: Sanity Page Config table

<template>
  <v-expansion-panels focusable class="sanity_summary">
    <v-expansion-panel>
      <v-expansion-panel-header>Sanity Run Summary</v-expansion-panel-header>
      <v-expansion-panel-content>
        <div>
          <h4>Run ID: {{ run_id }}</h4>
          <h4 style="display: inline">User: </h4>
          <p style="display: inline">{{ configData.User }}</p>
          <div>
            <h4 style="display: inline">
              Nodes ({{ configData.Nodes_Count }}):
            </h4>
            <p style="display: inline" v-if="configData && configData.Nodes">
              {{ configData.Nodes.join(", ") }}
            </p>
          </div>
          <div>
            <h4 style="display: inline">
              Clients ({{ configData.Clients_Count }}):
            </h4>
            <p style="display: inline" v-if="configData && configData.Clients">
              {{ configData.Clients.join(", ") }}
            </p>
          </div>
          <div>
            <h4 style="display: inline">Cluster Fill: </h4>
            <p style="display: inline">{{ configData.Cluster_Fill }}%</p>
          </div>
        </div>

        <v-card v-if="headers && headers.length > 0">
          <SanityDataTable
            TableName="Data"
            v-if="dataSummaryRead && dataSummaryRead.length > 0"
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
      configData: {},
      run_id: this.$route.query.run_id,
      headers: [],
      dataSummaryTput: [],
      dataSummaryRead: [],
      dataSummaryWrite: [],
    };
  },
  mounted() {
    sanityapi.fetchDataFromResponse(this.run_id, "config").then((response) => {
      this.configData = response.data;
    });

    sanityapi.fetchDataFromResponse(this.run_id, "others").then((response) => {
      this.dataSummaryTput = response.data.result;
      this.headers = sanityapi.getHeaderOfSanityfromObjects(
        this.dataSummaryTput
      );
      this.dataSummaryRead = sanityapi.getDataForSanityTables(
        this.dataSummaryTput.read
      );
      this.dataSummaryWrite = sanityapi.getDataForSanityTables(
        this.dataSummaryTput.write
      );
    });
  },
};
</script>

<style>
.sanity_summary {
  padding-left: 20px;
  padding-right: 20px;
}
</style>