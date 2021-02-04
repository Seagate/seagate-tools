<template>
  <div class="eos-p-2">
    <h1>Access Denied</h1>
    <p>
      This is a secure area. You are not authorized to see this page.
    </p>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
@Component({
  name: "eos-unauthorized-access"
})
export default class EosUnauthorizedAccess extends Vue {}
</script>
