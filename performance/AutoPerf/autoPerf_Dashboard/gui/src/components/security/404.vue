<template>
  <div class="eos-p-2">
    <h1>(404) Page Not Found</h1>
    <p>
      The page you are looking for does not exist.
    </p>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
@Component({
  name: "eos-not-found"
})
export default class EosNotFound extends Vue {}
</script>
