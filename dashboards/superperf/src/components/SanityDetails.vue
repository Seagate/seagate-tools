<template>
  <v-container>
    <v-card>
      <SanityDataTable
        TableName="Throughput"
        :Headers="headers"
        :DataValuesRead="DataValuesRead"
        :DataValuesWrite="DataValuesWrite"
      />
      <SanityDataTable
        TableName="Latency"
        :Headers="headers"
        :DataValuesRead="DataValuesRead"
        :DataValuesWrite="DataValuesWrite"
      />
      <SanityDataTable
        TableName="IOPS"
        :Headers="headers"
        :DataValuesRead="DataValuesRead"
        :DataValuesWrite="DataValuesWrite"
      />
      <SanityDataTable
        TableName="TTFB"
        :Headers="headers"
        :DataValuesRead="DataValuesRead"
        :DataValuesWrite="DataValuesWrite"
      />
    </v-card>
  </v-container>
</template>

<script>
import SanityDataTable from "./SanityDataTable.vue";

export default {
  name: "SanityDetailsPage",
  components: {
    SanityDataTable,
  },

  data: () => ({
    headers: [
      { text: "Index", value: "index" },
      { text: "1 KB", value: "1KB" },
      { text: "2 KB", value: "2KB" },
      { text: "3 KB", value: "3KB" },
    ],
    DataValuesRead: [
      {
        index: "Baseline",
        "1KB": 100,
        "2KB": 101,
        "3KB": 102,
      },
      {
        index: "Data",
        "1KB": 90,
        "2KB": 91,
        "3KB": 92,
      },
      {
        index: "Difference",
        "1KB": 10,
        "2KB": 10,
        "3KB": 10,
      },
      {
        index: "Deviation",
        "1KB": 10,
        "2KB": 10,
        "3KB": 10,
      },
    ],
    DataValuesWrite: [
      {
        index: "Baseline",
        "1KB": 100,
        "2KB": 101,
        "3KB": 102,
      },
      {
        index: "Data",
        "1KB": 90,
        "2KB": 91,
        "3KB": 92,
      },
      {
        index: "Diff",
        "1KB": 10,
        "2KB": 10,
        "3KB": 10,
      },
      {
        index: "Deviation",
        "1KB": 10,
        "2KB": 10,
        "3KB": 10,
      },
    ],
  }),
};
</script>