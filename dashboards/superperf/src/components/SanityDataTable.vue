<template>
  <v-container>
    <v-row>
      <v-col>
        <h3>Read {{ TableName }}</h3>
        <v-row>
          <v-col>
            <v-data-table
              :headers="Headers"
              :items="DataValuesRead"
              class="elevation-2"
              hide-default-footer
            >
            </v-data-table>
          </v-col>
        </v-row>
      </v-col>

      <v-col>
        <h3>Write {{ TableName }}</h3>
        <v-row>
          <v-col>
            <v-data-table
              :headers="Headers"
              :items="DataValuesWrite"
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
    DataValuesRead: Array,
    DataValuesWrite: Array,
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