<template>
  <v-app>
    <v-main>
      <MainHeader/>
      <SanitySummary/>
      <SanityDetails/>
    </v-main>
  </v-app>
</template>

<script>
import MainHeader from './components/MainHeader.vue'
import SanityDetails from './components/SanityDetails.vue'
import SanitySummary from './components/SanitySummary.vue'

export default {
  name: 'App',

  components: {
    MainHeader,
    SanitySummary,
    SanityDetails
  },

  data: () => ({
    //
  }),
}
</script>
