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
// Seagate-tools: Sanity componet for fetching all Performance Metrix View

<template>
  <v-container>
    <v-row>
      <v-col>
        <h3>{{ TableName }}</h3>
        <v-row>
          <v-col>
            <v-data-table
              :headers="Headers"
              :items="DataValues"
              class="elevation-2"
              hide-default-footer
            >
            </v-data-table>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    TableName: String,
    Headers: Array,
    DataValues: Array,
  },
  data() {
    return {
      //
    };
  },
};
</script>

<style lang="scss" scoped>
.v-data-table::v-deep th {
  font-size: 16px !important;
  background-color: #ced2d6;
}
</style>
