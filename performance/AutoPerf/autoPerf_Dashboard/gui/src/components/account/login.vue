<template>
  <div class="ms-sso">
    <div class="bg-datasphere-box motion m3">
      <div class="bg-datasphere layer-1"></div>
      <div class="bg-datasphere layer-2"></div>
      <div class="bg-datasphere layer-3"></div>
      <div class="bg-datasphere layer-4"></div>
    </div>

    <div class="container">
      <div class="content">
        <div class="logo">
          <embed
            type="image/svg+xml"
            :src="
              require('@/assets/login/stx-staticlogo-vertical-green-nopad-72x60.svg')
            "
            alt="Seagate"
          />
        </div>
        <div class="eos-brand-label">
          <span>AUTO PERF</span>
        </div>
        <div class="errors">
          <label></label>
        </div>

        <div class="sso-form">
          <v-text-field
            label="GID*"
            v-model.trim="loginForm.gid"
            :rules="[loginFormValidators.gid.required]"
            outlined
          ></v-text-field>
          <v-text-field
            type="password"
            label="Password*"
            v-model.trim="loginForm.password"
            :rules="[loginFormValidators.password.required]"
            outlined
          ></v-text-field>
          <v-btn
            color="primary"
            @click="login()"
            style="width: 100%;"
            :disabled="$v.loginForm.$invalid || loginInProgress"
          >Login</v-btn>
        </div>

        <div
          v-if="!isValidLogin"
          class="eos-text-alert mt-1 ml-4"
          style="text-align: center;"
        >
          Login failed !
        </div>
        <div class="secondary" style="margin-top: 10px;">
          <p style="background-color: #ffffff;">
            <router-link to="/register">Create your account.</router-link>
          </p>
        </div>
      </div>
      <div class="background"></div>
      <div class="backdrop"></div>
      <!-- start of vmv -->
      <div class="vmv-all vmv-motion"></div>
      <!-- end of vmv -->
    </div>

    <!-- Start Footer Simple-->
    <div class="footer">
      <div class="legal">
        <p>
          This is a Seagate computer system. Authorized access only. Access and
          use of this system constitutes consent to system monitoring by Seagate
          for law enforcement and other purposes. Unauthorized use of this
          computer system may subject you to criminal prosecution and penalties.
        </p>
        <p>Contact the IT Service Desk for assistance.</p>
      </div>
      <div class="copy">
        <p>
          © 2020 Seagate Technology LLC
        </p>
      </div>
    </div>
    <!-- End Footer Simple -->
  </div>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Validations } from "vuelidate-property-decorators";
import { required } from "vuelidate/lib/validators";
import { Api } from "../../services/api";
import apiRegister from "../../services/api-register";

@Component({
  name: "auto-perf-login"
})
export default class AutoPerfLogin extends Vue {
  public loginForm = {
    gid: "",
    password: ""
  };
  public isValidLogin: boolean = true;
  public loginInProgress: boolean = false;

  @Validations()
  public validations = {
    loginForm: {
      gid: { required },
      password: { required }
    }
  };

  public loginFormValidators = {
    gid: { required: (value: any) => !!value || "GID is required" },
    password: { required: (value: any) => !!value || "Password is required" }
  };

  public data() {
    return {
      constStr: require("./../../common/const-string.json")
    };
  }

  public mounted() {
    this.$store.dispatch("systemConfig/hideLoader");
    this.$store.commit("messageDialog/hide");
    this.$store.commit("userLogin/setUserPermissions", {});
  }

  public handleEnterEvent() {
    if (
      this.$v.loginForm &&
      !this.$v.loginForm.$invalid &&
      !this.loginInProgress
    ) {
      this.login();
    }
  }

  public async login() {
    // Hide login err message
    this.isValidLogin = true;
    this.loginInProgress = true;

    try {
      const res: any = await Api.post(apiRegister.login, {
        gid: this.loginForm.gid,
        password: this.loginForm.password
      });
      const user: any = {
        gid: this.loginForm.gid
      };

      if (res.data.result.token) {
        localStorage.setItem(
          this.$data.constStr.access_token,
          res.data.result.token
        );
        localStorage.setItem(this.$data.constStr.gid, user.gid);
        this.$router.push("/");
      } else {
        this.isValidLogin = false;
        throw new Error("Login Failed");
      }
    } catch (error) {
      // Show error message on screen
      this.isValidLogin = false;
      this.loginInProgress = false;
      throw new Error("Login Failed");
    }
  }
}
</script>

<style lang="scss" scoped>
.eos-brand-label {
  color: #6ebe49;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}
a {
  color: #6ebe49;
  text-decoration: none;
  &:hover,
  &:focus {
    color: #4b813d;
    text-decoration: underline;
  }
  &:active,
  &.active {
    color: #2d8f00;
  }
}
p {
  margin: 0 0 0.875rem;
}
.ms-sso {
  position: relative;
}
.ms-sso .validation,
.ms-sso .sso-form,
.ms-sso .secondary {
  max-width: 25rem;
  margin: 0 auto;
}
.ms-sso .validation {
  text-align: center;
  margin-bottom: 1.333333333333333rem;
}
.ms-sso .validation p {
  font-size: 0.875rem;
  line-height: 1.35rem;
}
.ms-sso .validation p:last-child {
  margin-bottom: 0;
}
.ms-sso .validation:empty {
  margin-bottom: 0;
}
.ms-sso .container {
  position: relative;
  z-index: 5;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 200px);
  overflow: hidden;
}
@media (min-width: 768px) {
  .ms-sso .container {
    padding: 0;
    height: 45rem;
    min-height: calc(100vh - 136px);
  }
}
.ms-sso .content {
  position: relative;
  z-index: 10;
}
@media (min-width: 768px) {
  .ms-sso .content {
    width: 560px;
    height: 560px;
    width: 35rem;
    height: 35rem;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    margin: -17.5rem 0 0 -17.5rem;
  }
}
.ms-sso .background {
  width: 35rem;
  height: 35rem;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  margin: -17.5rem 0 0 -17.5rem;
  background-color: #fff;
}
.ms-sso .background:after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #6ebe49;
  z-index: -1;
  -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";
  filter: alpha(opacity=0);
  opacity: 0;
}
@media (min-width: 768px) {
  .ms-sso .backdrop {
    position: absolute;
    left: 50%;
    top: 50%;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
    width: 640px;
    height: 640px;
    width: 40rem;
    height: 40rem;
    z-index: 1;
    margin: -20rem 0 0 -20rem;
  }
}
.ms-sso .logo {
  text-align: center;
  padding: 40px 0;
}
@media (min-width: 768px) {
  .ms-sso .logo {
    padding: 2.75rem 0 1rem;
  }
}
.ms-sso .logo img {
  width: 72px;
  height: 60px;
  outline: 0;
  border: 0;
}
.ms-sso .logo embed {
  width: 72px;
  height: 60px;
  outline: 0;
  border: 0;
}
.ms-sso .form-control:hover,
.ms-sso .form-control:focus,
.ms-sso .form-control.focus,
.ms-sso .form-control.active,
.ms-sso .form-control:active {
  -webkit-transition: border-color linear 0.2s, box-shadow linear 0.2s;
  transition: border-color linear 0.2s, box-shadow linear 0.2s;
}
.ms-sso .btn {
  display: block;
  width: 100%;
  font-size: 1rem;
  font-weight: bold;
  line-height: 3rem;
  padding: 0 1.5rem;
  margin-bottom: 0;
  text-align: center;
  text-transform: uppercase;
  touch-action: manipulation;
  cursor: pointer;
  white-space: nowrap;
  border: 0;
  border-radius: 3px;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  height: 3rem;
  overflow: hidden;
  text-overflow: ellipsis;
  background-color: #6ebe49;
  color: #ffffff;
  text-shadow: none;
}
.ms-sso .btn:hover,
.ms-sso .btn:focus,
.ms-sso .btn.focus,
.ms-sso .btn.active,
.ms-sso .btn:active {
  -webkit-transition: background-color 0.2s, color 0.2s;
  transition: background-color 0.2s, color 0.2s;
  background-color: #4b813d;
  border-color: transparent;
  text-decoration: none;
  outline: 0;
}
.ms-sso .btn.disabled,
.ms-sso .btn[disabled],
.ms-sso .btn.disabled:hover,
.ms-sso .btn[disabled]:hover,
.ms-sso .btn.disabled:focus,
.ms-sso .btn[disabled]:focus,
.ms-sso .btn.disabled.focus,
.ms-sso .btn[disabled].focus,
.ms-sso .btn.disabled:active,
.ms-sso .btn[disabled]:active,
.ms-sso .btn.disabled.active,
.ms-sso .btn[disabled].active {
  background-color: #eee;
  color: #bbb;
  cursor: not-allowed;
  pointer-events: all;
  text-shadow: none;
}
.ms-sso .eos-btn-primary.loading {
  background-image: url(../../assets/login/seagate-spinner-23.gif);
  background-repeat: no-repeat;
  background-position: center;
  color: transparent !important;
  font-size: 0;
}
.ms-sso .secondary {
  text-align: center;
}
.ms-sso .secondary p {
  font-weight: normal;
  font-size: 1rem;
  line-height: 1.5rem;
  padding: 0.2rem 0;
  margin: 0;
}
@media (min-width: 768px) {
  .ms-sso .secondary p {
    line-height: 1.35rem;
    font-size: 0.875rem;
  }
}
.ms-sso .footer {
  padding: 24px 24px 0;
  margin: 0 auto;
  text-align: center;
  min-height: 200px;
}
@media (min-width: 768px) {
  .ms-sso .footer {
    min-height: 136px;
    max-width: 640px;
    padding: 24px 0 0;
  }
}
.ms-sso .footer p {
  font-size: 12px;
  line-height: 16px;
  margin: 0 0 12px;
}
.ms-sso .footer .legal {
  color: #888;
}
.ms-sso .footer .copy {
  color: #c6c6c6;
}
.ms-sso .footer .copy p {
  margin-bottom: 0;
}
.help-block {
  font-size: 1rem;
  line-height: 1.35rem;
  padding: 0.182142857142857rem 0;
  margin-bottom: 0.2857142857142857rem;
  color: #808080;
}
@media (min-width: 1200px) {
  .help-block {
    font-size: 0.875rem;
  }
}
.form-group {
  position: relative;
  margin-bottom: 1.333333333333333rem;
}
.form-group:before,
.form-group:after {
  content: " ";
  display: table;
}
.form-group:after {
  clear: both;
}
.form-group.has-warning .form-control {
  border-color: #ff5000;
}
.form-group.has-warning .form-control:focus {
  border-color: #cc4000;
}
.form-group.has-error .form-control {
  border-color: #dc1f2e;
}
.form-group.has-error .form-control:focus {
  border-color: #af1925;
}
label {
  display: inline-block;
  max-width: 100%;
  font-weight: normal;
  font-size: 1rem;
  line-height: 1.35rem;
  padding: 0.182142857142857rem 0;
  margin-bottom: 0.2857142857142857rem;
}
@media (min-width: 1200px) {
  label {
    font-size: 0.875rem;
  }
}
label + .help-block {
  margin-top: 0;
}
label.focused {
  color: #333333;
  font-weight: bold;
  transition: color 0.3s;
}
.checkbox-custom + label,
.radio-custom + label {
  font-size: 1rem;
  line-height: 1.35;
  padding: 0 0 0 2rem;
  margin-bottom: 0;
  color: #333;
}
.form-control {
  display: block;
  width: 100%;
  font-size: 1rem;
  line-height: 3rem;
  padding: 0 1rem;
  height: 3rem;
  color: #333333;
  background-color: #ffffff;
  background-image: none;
  border: 1px solid #c6c6c6;
  border-radius: 3px;
}
.form-control + .help-block {
  margin-top: 0.2857142857142857rem;
}
.form-control:focus {
  border-color: #595959;
  outline: 0;
  transition: background-color 0.3s;
}
textarea.form-control {
  height: auto;
}
.form-control-static {
  padding: 0;
  min-height: 0;
}
.password-text {
  display: none;
}
.select-box {
  position: relative;
}
.select-box select.form-control {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
.select-box select.form-control::-ms-expand {
  display: none;
}
.select-box select:focus + i {
  border-color: #595959 transparent transparent transparent;
}
.select-box i {
  position: absolute;
  top: 50%;
  right: 1rem;
  -webkit-transform: translate(0, -50%);
  -ms-transform: translate(0, -50%);
  transform: translate(0, -50%);
  -webkit-transition: border-color 0.3s;
  transition: border-color 0.3s;
  width: 0;
  height: 0;
  pointer-events: none;
  border-style: solid;
  border-width: 8px 5px 0 5px;
  border-color: #c6c6c6 transparent transparent transparent;
}
.has-success .validation-message,
.has-warning .validation-message,
.has-error .validation-message {
  font-size: 1rem;
  line-height: 1.35rem;
  padding: 0.182142857142857rem 0;
}
@media (min-width: 1200px) {
  .has-success .validation-message,
  .has-warning .validation-message,
  .has-error .validation-message {
    font-size: 0.875rem;
  }
}
.has-success select ~ .validation-message,
.has-warning select ~ .validation-message,
.has-error select ~ .validation-message,
.has-success input ~ .validation-message,
.has-warning input ~ .validation-message,
.has-error input ~ .validation-message,
.has-success .input-group ~ .validation-message,
.has-warning .input-group ~ .validation-message,
.has-error .input-group ~ .validation-message {
  margin-top: 0.2857142857142857rem;
}
@media (min-width: 768px) {
  .bg-datasphere-box {
    position: absolute;
    z-index: 1;
    background: url(../../assets/login/bg-datasphere-stacked-transparent-1140x1080.png)
      no-repeat center;
    background-size: 71.25rem 67.5rem;
    width: 100%;
    height: 100%;
    top: -2rem;
  }
}
@media (min-width: 992px) {
  .bg-datasphere-box {
    top: -1.8rem;
  }
}
@media (min-width: 1200px) {
  .bg-datasphere-box {
    top: -1.7rem;
  }
}
@media (min-width: 1600px) {
  .bg-datasphere-box {
    top: -1.6rem;
  }
}
@supports (animation-name: zoomIn) {
  @media (min-width: 768px) {
    .bg-datasphere-box.motion {
      background: none;
      overflow: hidden;
    }
    .bg-datasphere-box.motion .bg-datasphere {
      background-size: 71.25rem 67.5rem;
      background-repeat: no-repeat;
      background-position: center;
      position: absolute;
      width: 100%;
      height: 100%;
      top: -3.5rem;
      will-change: transform, opacity;
      opacity: 0;
    }
    .bg-datasphere-box.motion .layer-1 {
      background-image: url(../../assets/login/bg-datasphere-layer-1-transparent-1140x1080.png);
    }
    .bg-datasphere-box.motion .layer-2 {
      background-image: url(../../assets/login/bg-datasphere-layer-2-transparent-1140x1080.png);
    }
    .bg-datasphere-box.motion .layer-3 {
      background-image: url(../../assets/login/bg-datasphere-layer-3-transparent-1140x1080.png);
    }
    .bg-datasphere-box.motion .layer-4 {
      background-image: url(../../assets/login/bg-datasphere-layer-4-transparent-1140x1080.png);
    }
  }
  @media (min-width: 992px) {
    .bg-datasphere-box.motion .bg-datasphere {
      top: -3.2rem;
    }
  }
  @media (min-width: 1200px) {
    .bg-datasphere-box.motion .bg-datasphere {
      top: -3rem;
    }
  }
  @media (min-width: 1600px) {
    .bg-datasphere-box.motion .bg-datasphere {
      top: -2.6rem;
    }
  }
  @media (min-width: 768px) {
    .bg-datasphere-box.m1 .bg-datasphere {
      animation: 3s forwards zoomIn;
    }
    .bg-datasphere-box.m1 .layer-2 {
      animation-delay: 0.33s;
    }
    .bg-datasphere-box.m1 .layer-3 {
      animation-delay: 0.66s;
    }
    .bg-datasphere-box.m1 .layer-4 {
      animation-delay: 1s;
    }
  }
  @media (min-width: 768px) {
    .bg-datasphere-box.m2 .bg-datasphere {
      animation: 3s forwards zoomRotate-1;
    }
    .bg-datasphere-box.m2 .layer-2 {
      animation-name: zoomRotate-2;
      animation-delay: 0.33s;
    }
    .bg-datasphere-box.m2 .layer-3 {
      animation-name: zoomRotate-3;
      animation-delay: 0.66s;
    }
    .bg-datasphere-box.m2 .layer-4 {
      animation-name: zoomRotate-4;
      animation-delay: 1s;
    }
  }
  @media (min-width: 768px) {
    .bg-datasphere-box.m3 .bg-datasphere {
      animation-timing-function: cubic-bezier(0.13, 0.35, 0.18, 1);
      animation-timing-function: cubic-bezier(0.35, 0.05, 0.58, 0.96);
      animation-timing-function: cubic-bezier(0.29, 0, 0.67, 1);
      animation-timing-function: cubic-bezier(0.45, 0, 0.45, 1);
      animation-fill-mode: forwards;
    }
    .bg-datasphere-box.m3 .layer-1 {
      animation-name: zoomRotate-1;
      animation-duration: 2s;
      animation-delay: 0.8s;
    }
    .bg-datasphere-box.m3 .layer-2 {
      animation-name: zoomRotate-2;
      animation-duration: 2.2s;
      animation-delay: 0.6s;
    }
    .bg-datasphere-box.m3 .layer-3 {
      animation-name: zoomRotate-3;
      animation-duration: 2.4s;
      animation-delay: 0.4s;
    }
    .bg-datasphere-box.m3 .layer-4 {
      animation-name: zoomRotate-4;
      animation-duration: 2.8s;
      animation-delay: 0s;
    }
    .bg-datasphere-box.m3 + .container .background {
      animation: 2.4s forwards zoomBitIn cubic-bezier(0.45, 0, 0.45, 1);
    }
    .bg-datasphere-box.m3 + .container .backdrop {
      animation: 2.8s forwards scaleIn cubic-bezier(0.45, 0, 0.45, 1);
    }
  }
  .entering.ms-sso .bg-datasphere-box.m3 .layer-1,
  .entering.ms-sso .bg-datasphere-box.m3 .layer-2,
  .entering.ms-sso .bg-datasphere-box.m3 .layer-3,
  .entering.ms-sso .bg-datasphere-box.m3 .layer-4 {
    animation-name: zoomInReverse;
    animation-duration: 0.6s;
    animation-delay: 0s;
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .container .content {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .container .background {
    animation: 0.6s forwards zoomOutContentBG cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .container .background:after {
    animation: 0.6s 0.6s infinite forwards alternate loadingUp
      cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .container .backdrop {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .idframe .container .content {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .idframe .container .background {
    animation: 0.6s forwards zoomOutContentBG cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso
    .bg-datasphere-box.m3
    + .idframe
    .container
    .background:after {
    animation: 0.6s 0.6s infinite forwards alternate loadingUp
      cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .idframe .container .backdrop {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
}
@keyframes loadingUp {
  0% {
    transform: scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  100% {
    transform: scale(1.35);
    opacity: 1;
  }
}
@keyframes zoomOutContentBG {
  0% {
    background-color: #fff;
    transform: scale(1);
    z-index: 2;
    opacity: 1;
  }
  10% {
    z-index: 11;
  }
  60% {
    background-color: #6ebe49;
  }
  100% {
    background-color: #6ebe49;
    transform: scale(0.03);
    opacity: 1;
  }
}
@keyframes zoomIn {
  0% {
    transform: scale(0.1) rotate(0deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
@keyframes zoomInReverse {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  to {
    transform: scale(0) rotate(0deg);
    opacity: 0;
  }
}
@keyframes zoomRotate-1 {
  0% {
    transform: scale(0.1) rotate(-180deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
@keyframes zoomRotate-2 {
  0% {
    transform: scale(0.1) rotate(-135deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
@keyframes zoomRotate-3 {
  0% {
    transform: scale(0.1) rotate(-90deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
@keyframes zoomRotate-4 {
  0% {
    transform: scale(0.1) rotate(-22.5deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
@keyframes zoomBitIn {
  0% {
    transform: scale(0.4);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}
@keyframes scaleInReverse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0);
    opacity: 0;
  }
}
.customPForEnv {
  padding: 0.3rem;
  padding-bottom: 0;
  margin-bottom: 0;
}

.customSpanForEnv {
  font-size: 0.875rem;
  color: #6ebe49;
  line-height: 1em;
  display: inline-block;
  vertical-align: top;
  border-radius: 9999em;
  border-width: 1px;
  border-style: solid;
  border-color: #6ebe49;
  border-image: initial;
  padding: 0.3em 0.8em;
}
@media (min-width: 768px) {
  .vmv-all {
    position: absolute;
    left: 50%;
    top: 50%;
    background: url(../../assets/login/vmv-sso-640x640-all.png) no-repeat center;
    background-size: contain;
    width: 640px;
    height: 640px;
    width: 40rem;
    height: 40rem;
    z-index: 4;
    margin: -20rem 0 0 -20rem;
  }
}
@supports (animation-name: zoomIn) {
  @media (min-width: 768px) {
    .vmv-static {
      opacity: 0;
      animation: 0.8s forwards fadeIn cubic-bezier(0.45, 0, 0.45, 1) 2.4s;
    }
  }
  @media (min-width: 768px) {
    .vmv-motion {
      transform: rotate(-45deg);
      opacity: 0;
      animation: 1.2s forwards rotateVMV cubic-bezier(0.45, 0, 0.45, 1) 1.8s;
    }
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .container .vmv-all {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
  .entering.ms-sso .bg-datasphere-box.m3 + .idframe .container .vmv-all {
    animation: 0.6s forwards scaleInReverse cubic-bezier(0.45, 0, 0.45, 1);
  }
}
@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes rotateVMV {
  0% {
    transform: rotate(-45deg);
    opacity: 0;
  }
  to {
    transform: rotate(0deg);
    opacity: 1;
  }
}
</style>
