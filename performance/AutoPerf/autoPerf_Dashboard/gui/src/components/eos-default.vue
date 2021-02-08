<template>
  <div>
    <v-app-bar color="#ffffff" dense>
      <img
        class="eos-brand-logo"
        :src="
          require('@/assets/registration/stx-staticlogo-green-nopad-109x26.png')
        "
      />
      <div class="eos-logo-separator"></div>
      <v-toolbar-title style="color: #6ebe49;">Auto Perf</v-toolbar-title>
      <v-spacer></v-spacer>
      <label class="eos-username-label">{{ username }}</label>
      <div
        class="eos-logout-icon-container"
        @click="logout()"
      >
        <v-tooltip left max-width="300">
          <template v-slot:activator="{ on }">
            <img :src="require('@/assets/logout.svg/')" v-on="on" />
          </template>
          <span>Logout</span>
        </v-tooltip>
      </div>
    </v-app-bar>
    <router-view></router-view>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import VueNativeSock from "vue-native-websocket";
import store from "../store/store";

@Component({
  name: "Default"
})
export default class EosDefault extends Vue {
  public username: string = "";

  public mounted() {
    const usernameStr = localStorage.getItem("gid");
    if (usernameStr) {
      this.username = usernameStr;
    }
  }

  public logout() {
    // Invalidate session from Server, remove localStorage token and re-route to login page
    localStorage.removeItem("access-token");
    localStorage.removeItem("username");
    this.$router.push("/login");
  }
}
</script>

<style lang="scss" scoped>
.header-margin {
  margin-top: 7em;
}
.navbar-margin {
  margin-left: 8.75em;
}
.eos-brand-logo {
  height: fit-content;
  width: fit-content;
}
.eos-logo-separator {
  border: 1px solid #eaeaea;
  height: 35px;
  margin-left: 1em;
  margin-right: 1em;
}
.eos-logout-icon-container {
  margin-right: 10px;
  margin-top: 5px;
  cursor: pointer;
}
.eos-username-label {
  margin-right: 20px;
  color: #6ebe49;
}
</style>
