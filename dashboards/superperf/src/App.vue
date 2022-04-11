<template>
  <v-app>
    <v-main>
      <MainHeader/>
      <SanityDetails/>
    </v-main>
  </v-app>
</template>

<script>
import MainHeader from './components/MainHeader.vue'
import SanityDetails from './components/SanityDetails.vue'

export default {
  name: 'App',

  components: {
    MainHeader,
    SanityDetails
  },

  data: () => ({
    //
  }),
}
</script>
