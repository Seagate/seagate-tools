import "@mdi/font/css/materialdesignicons.css";
import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "mdi"
  },
  theme: {
    options: {
      customProperties: true
    },
    themes: {
      light: {
        primary: "#6ebe49",
        secondary: "#424242",
        accent: "#82B1FF",
        error: "#dc1f2e",
        info: "#2196F3",
        success: "#4CAF50",
        warning: "#FFC107",
      }
    }
  }
});
