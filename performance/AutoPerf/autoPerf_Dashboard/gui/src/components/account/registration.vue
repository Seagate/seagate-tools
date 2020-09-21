<template>
  <div style="background-color: #ffffff;">
    <div class="eos-header-container">
      <div class="eos-header">
        <img
          class="eos-brand-logo"
          :src="
            require('@/assets/registration/stx-staticlogo-green-nopad-109x26.png')
          "
        />
        <div class="eos-logo-separator"></div>
        <div class="eos-brand-label">
          <span style="font-weight: bold;">AUTO PERF</span>
        </div>
      </div>
    </div>
    <div class="pn-container pn-no-nav">
      <div class="portal-nav">
        <div class="pn-title">
          <h3>Create Account</h3>
        </div>
      </div>
    </div>
    <div class="ma-container">
      <div class="container">
        <div class="row" style="margin-top: 4.5em;">
          <div class="col-md-3">
            <div class="ma-side-intro body-small">
              <p>Welcome to Auto Perf application.</p>
              <p>Manage your account which gives you access to the auto perf application.</p>
              <p>
                If you need any help with your Account, contact the IT Service
                Desk.
              </p>
              <p>
                Already have account?<router-link to="/login" style="margin-left: 10px;">Login here</router-link>
              </p>
            </div>
          </div>
          <div class="col-md-9" style="padding-left: 25px;">
            <v-row style="margin-top: 30px;">
              <v-col class="py-0 pr-0">
                <div class="eos-form-group">
                  <v-text-field
                    label="GID*"
                    v-model.trim="registrationForm.gid"
                    :rules="[registrationFormValidators.gid.required]"
                    outlined
                    dense
                  ></v-text-field>
                </div>
              </v-col>
              <v-col class="py-0 pl-0">
                <div class="eos-form-group">
                  <v-text-field
                    label="Email id*"
                    v-model.trim="registrationForm.email"
                    :rules="[registrationFormValidators.email.required, registrationFormValidators.email.email]"
                    outlined
                    dense
                  >
                  </v-text-field>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0 pr-0">
                <div class="eos-form-group">
                  <v-text-field
                    type="password"
                    label="Password*"
                    v-model.trim="registrationForm.password"
                    :rules="[registrationFormValidators.password.required, registrationFormValidators.password.password]"
                    outlined
                    dense
                  ></v-text-field>
                </div>
              </v-col>
              <v-col class="py-0 pl-0">
                <div class="eos-form-group">
                  <v-text-field
                    type="password"
                    label="Confirm Password*"
                    v-model.trim="registrationForm.confirmPassword"
                    :rules="[registrationFormValidators.confirmPassword.required, registrationFormValidators.confirmPassword.sameAsPassword]"
                    outlined
                    dense
                  ></v-text-field>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0 pr-0">
                <div class="eos-form-group">
                  <v-text-field
                    label="Full name*"
                    v-model.trim="registrationForm.full_name"
                    :rules="[registrationFormValidators.full_name.required]"
                    outlined
                    dense
                  >
                  </v-text-field>
                </div>
              </v-col>
              <v-col class="py-0 pl-0">
                <div class="eos-form-group">
                  <v-text-field
                    label="Team name*"
                    v-model.trim="registrationForm.team_name"
                    :rules="[registrationFormValidators.team_name.required]"
                    outlined
                    dense
                  >
                  </v-text-field>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0 pr-0">
                <div class="eos-form-group">
                  <v-select
                    :items="componentList"
                    item-text="label"
                    item-value="value"
                    v-model="registrationForm.component"
                    label="Component*"
                    outlined
                    dense
                  ></v-select>
                </div>
              </v-col>
              <v-col class="py-0 pl-0">
                <div class="eos-form-group">
                  <v-select
                    :items="roleList"
                    item-text="label"
                    item-value="value"
                    v-model="registrationForm.role"
                    label="Role*"
                    outlined
                    dense
                  ></v-select>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0 pr-0">
                <div class="eos-form-group">
                  <v-select
                    :items="managerList"
                    item-text="label"
                    item-value="value"
                    v-model="registrationForm.manager"
                    label="Manager*"
                    outlined
                    dense
                  ></v-select>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="py-0">
                <v-btn
                  color="primary"
                  @click="register()"
                  :disabled="$v.registrationForm.$invalid"
                >Register</v-btn>
                <v-btn
                  color="primary"
                  @click="clearRegistrationForm()"
                  style="margin-left: 16px;"
                  outlined
                >Clear</v-btn>
                <div
                  v-if="!isRegistrationSuccessful"
                  class="eos-text-alert mt-2 ml-4"
                  style="margin-top:8px;"
                >{{ registrationFailedMsg }}</div>
              </v-col>
            </v-row>
          </div>
        </div>
      </div>
    </div>
    <v-dialog
      v-model="isRegistrationSuccessful"
      width="500"
    >
      <v-card>
        <v-card-title class="headline" style="background-color: #6ebe49; color: #ffffff;">
          Account Created
        </v-card-title>

        <v-card-text style="margin-top: 15px;">
          Account created successfully. Please login to continue.
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="closeRegResponseDetailsDialog()"
          >
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Validations } from "vuelidate-property-decorators";
import { required, sameAs, email } from "vuelidate/lib/validators";
import { passwordRegex } from "../../common/regex-helpers";
import { Api } from "../../services/api";
import apiRegister from "../../services/api-register";

@Component({
  name: "auto-perf-registration"
})
export default class AutoPerfRegistration extends Vue {
  public roleList = [
    {
      label: "Developer",
      value: "dev"
    },
    {
      label: "QA",
      value: "qa"
    }
  ];

  public managerList: any[] = [];
  public componentList: any[] = [];

  public registrationForm = {
    gid: "",
    email: "",
    component: "",
    team_name: "",
    manager: "",
    role: "",
    password: "",
    confirmPassword: "",
    full_name: ""
  };

  public isRegistrationSuccessful: boolean = false;
  public registrationFailedMsg: string = "";

  @Validations()
  public validations = {
    registrationForm: {
      gid: { required },
      email: { required, email },
      component: { required },
      team_name: { required },
      manager: { required },
      role: { required },
      password: { required, passwordRegex },
      confirmPassword: {
        sameAsPassword: sameAs("password")
      },
      full_name: { required }
    }
  };

  public registrationFormValidators = {
    gid: { required: (value: any) => !!value || "GID is required" },
    email: {
      required: (value: any) => !!value || "Email id is required",
      email: (value: any) => {
        const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return pattern.test(value) || "Invalid email id";
      }
    },
    password: {
      required: (value: any) => !!value || "Password is required",
      password: (value: any) => {
        const pattern = /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#\$%\^&\*\(\)\_\+\-\=\[\]\{\}\|\'])[A-Za-z\d!@#\$%\^&\*\(\)\_\+\-\=\[\]\{\}\|\']{8,}/;
        return pattern.test(value) || "Invalid password";
      }
    },
    confirmPassword: {
      required: (value: any) => !!value || "Confirm password is required",
      sameAsPassword: (value: any) => value === this.registrationForm.password || "Passwords do not match"
    },
    full_name: { required: (value: any) => !!value || "Full name is required" },
    team_name: { required: (value: any) => !!value || "Team name is required" }
  };

  public mounted() {
    Api.getAll(apiRegister.managers).then((resp) => {
      resp.data.result.data.forEach((manager: any) => {
        this.managerList.push({
          label: manager.name,
          value: manager._id
        });
      });
    });

    Api.getAll(apiRegister.components).then((resp) => {
      resp.data.result.data.forEach((component: any) => {
        this.componentList.push({
          label: component.name,
          value: component._id
        });
      });
    });
  }

  public async register() {
    try {
      this.$store.dispatch("systemConfig/showLoader", "Registering...");
      const res = await Api.post(apiRegister.user_registration, {
        gid: this.registrationForm.gid,
        email: this.registrationForm.email,
        component: this.registrationForm.component,
        team_name: this.registrationForm.team_name,
        manager_name: this.registrationForm.manager,
        role: this.registrationForm.role,
        password: this.registrationForm.password,
        full_name: this.registrationForm.full_name
      });

      if (res && (res.data.statusCode === 200 || res.data.statusCode === 201)) {
        this.isRegistrationSuccessful = true;
      } else {
        this.isRegistrationSuccessful = false;
        this.registrationFailedMsg = res.data.message;
      }
      this.$store.dispatch("systemConfig/hideLoader");
    } catch (e) {
      this.$store.dispatch("systemConfig/hideLoader");
      // tslint:disable-next-line: no-console
      console.error("err logger: ", e);
      throw new Error(e.message);
    }
  }

  public clearRegistrationForm() {
    this.registrationForm.gid = "";
    this.registrationForm.email = "";
    this.registrationForm.component = {} as any;
    this.registrationForm.team_name = "";
    this.registrationForm.manager = {} as any;
    this.registrationForm.role = {} as any;
    this.registrationForm.password = "";
    this.registrationForm.confirmPassword = "";
    this.registrationForm.full_name = "";
    this.registrationFailedMsg = "";
    if (this.$v.registrationForm) {
      this.$v.registrationForm.$reset();
    }
  }

  public closeRegResponseDetailsDialog() {
    this.$router.push("/login");
  }
}
</script>

<style lang="scss" scoped>
.eos-header-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 5;
  border-bottom: 1px solid #eaeaea;
  background: #fff;
}
.eos-header {
  display: flex;
  flex-wrap: nowrap;
  height: 3.5em;
}
.eos-logo-separator {
  border: 1px solid #eaeaea;
  margin: 0.7em;
}
.eos-brand-logo {
  margin-left: 3em;
  margin-top: 0.9em;
  height: fit-content;
  width: fit-content;
}
.eos-brand-label {
  color: #6ebe49;
  font-size: 18px;
  margin-top: 0.9em;
}
.pn-container {
  position: relative;
  background: none;
  top: 3.55em;
}
.pn-container.pn-no-nav {
  transition: margin 0.3s ease;
}
.portal-nav {
  height: auto;
  position: fixed;
  width: 100%;
  left: 0;
  right: 0;
  background: #6ebe49;
  -webkit-transition: top 0.3s ease;
  -o-transition: top 0.3s ease;
  transition: top 0.3s ease;
}
.pn-title {
  padding: 10px 10px 10px 60px;
  position: relative;
}
.pn-title > h3 {
  color: #ffffff;
}
.ma-container {
  min-height: calc(100vh - 54px - 56px - 23px - 100px - (63px - 54px));
}
@media (max-width: 991px) {
  .ma-container {
    min-height: calc(100vh - 49px - 49px - 15px - 100px - (63px - 54px));
  }
}
@media (max-width: 767px) {
  .ma-container {
    min-height: calc(100vh - 49px - 49px - 15px - 40px);
  }
}
@media (max-width: 567px) {
  .ma-container {
    min-height: calc(100vh - 49px - 95px - 15px - 40px);
  }
}
.ma-side-intro {
  padding: 100px 0 0 0;
  background: url("../../assets/registration/icn-side-intro.png") no-repeat 0
    13px;
}
@media (max-width: 991px) {
  .ma-side-intro {
    padding: 0 0 0 60px;
    margin-bottom: 15px;
    background-position: 10px 0;
    background-size: 33px 39px;
  }
}
.body-small {
  font-size: 14px;
  line-height: 1.3571428;
  margin-top: 10px;
  margin-bottom: 9.5px;
}
p {
  margin: 0 0 9.5px;
}
@media (min-width: 992px) {
  p {
    margin-bottom: 11.5px;
  }
}
.py-0 {
  padding-top: 0px;
  padding-bottom: 0px;
}
.pr-0 {
  padding-right: 0px;
}
.pl-0 {
  padding-left: 0px;
}
.eos-reg-response-container {
  height: 7.5em;
  border-bottom: 1px solid #b7b7b7;
  overflow: auto;
  padding: 16px;
}
.eos-modal-footer {
  height: 3.5em;
  padding: 0.5em;
}
</style>
