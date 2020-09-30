<script>
export default {
  functional: true,
  props: ["to"],
  render(h, { props, slots }) {
    if (Vue.prototype.$hasAccessToCsm(props.to)(props.to)) {
      return slots().default;
    }
    return h();
  }
};
</script>
