<!--
*  Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
*
*  This program is free software: you can redistribute it and/or modify
*  it under the terms of the GNU Affero General Public License as published
*  by the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*  GNU Affero General Public License for more details.
*  You should have received a copy of the GNU Affero General Public License
*  along with this program. If not, see <https:  www.gnu.org/licenses/>.
*
*  For any questions about this software or licensing,
*  please email opensource@seagate.com or cortx-questions@seagate.com.
*
*  -*- coding: utf-8 -*-
-->
// Seagate-tools: Main Header for SuperPerf UI

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
        font-family: Cambria, Cochin, Georgia, Times, "Times New Roman", serif;
    }
</style>
