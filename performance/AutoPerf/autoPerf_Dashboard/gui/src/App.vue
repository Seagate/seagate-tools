<template>
  <v-app style="background-color: #F4F5F7;">
    <router-view></router-view>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component({
  name: "App"
})
export default class App extends Vue {
}
</script>

<style lang="scss" scoped></style>
