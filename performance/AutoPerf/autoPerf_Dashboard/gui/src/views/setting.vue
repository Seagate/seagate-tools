<template>
  <eosUserSetting :buttonsShow="false" />
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import EosUserSetting from "./../components/onboarding/system-config/user-settings/user-setting-local.vue";

@Component({
  name: "eos-setting",
  components: {
    eosUserSetting: EosUserSetting
  }
})
export default class Setting extends Vue {}
</script>
<style lang="scss" scoped>
.page {
  position: relative;
}
</style>
