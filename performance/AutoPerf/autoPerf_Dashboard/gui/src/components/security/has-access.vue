<template>
  <span v-if="$hasAccessToCsm(to)">
    <slot></slot>
  </span>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
@Component({
  name: "eos-has-access"
})
export default class EosHasAccess extends Vue {
  @Prop({ required: true })
  public to: string;
}
</script>
