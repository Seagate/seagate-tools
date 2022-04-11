<template>
    <v-toolbar dense>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title class="header-title">SuperPerf</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-heart</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </v-toolbar>
</template>

<style lang="scss" scoped>
    .header-title {
        color: #6EBE49;
        font-weight: bold;
        font-size: 30px;
        font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
    }
</style>
