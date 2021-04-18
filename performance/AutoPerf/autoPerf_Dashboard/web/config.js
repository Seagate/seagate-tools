require("dotenv").config({ path: __dirname + "/.env" });
const dir = require("path").join(__dirname, "../../");

module.exports = {
  port: process.env[`${process.env.NODE_ENV}_PORT`],
  databaseHost: process.env[`${process.env.NODE_ENV}_DB_HOST`],
  databaseUser: process.env[`${process.env.NODE_ENV}_DB_USER`],
  databasePassword: process.env[`${process.env.NODE_ENV}_DB_PASSWORD`],
  databaseName: process.env[`${process.env.NODE_ENV}_DB_NAME`],
  databaseInitial: process.env[`${process.env.NODE_ENV}_DB_INITIAL`],
  database: "mongoDB",
  databasePort: process.env[`${process.env.NODE_ENV}_DB_PORT`],
  mongoDBConnectionString: process.env[`${process.env.NODE_ENV}_MONGO_DB_CONN_STRING`],
  emailVerificationLink:
    process.env[`${process.env.NODE_ENV}_EMAIL_VERIFICATION_LINK`],
  resetPasswordLink: process.env[`${process.env.NODE_ENV}_RESET_PASS_LINK`],
  tokenkey: "37LvPsm4vaBcd4CY",
  bodyEncryption: false,
  supportEmail: process.env[`${process.env.NODE_ENV}_SUPPORT_EMAIL`],
  SMTPemailAddress: process.env[`${process.env.NODE_ENV}_SMTP_EMAILADDRESS`],
  SMTPPassword: process.env[`${process.env.NODE_ENV}_SMTP_PASS`],
  cryptokey: process.env[`${process.env.NODE_ENV_DB_PASS}_CRYPTO_KEY`],
  awsBucket: process.env[`${process.env.NODE_ENV}_AWS_BUCKET`],
  awsAccessKey: process.env[`${process.env.NODE_ENV}_AWS_ACCESS_KEY`],
  awsSecretAccessKey:
    process.env[`${process.env.NODE_ENV}_AWS_SECRET_ACCESS_KEY`],
  hardwareAllocationJobCron:
    process.env[`${process.env.NODE_ENV}_HARDWARE_ALLOCATION_CRON`],
  hardwareReleaseJobCron:
    process.env[`${process.env.NODE_ENV}_HARDWARE_RELEASE_CRON`],
  daysDiffForComments:
    process.env[`${process.env.NODE_ENV}_DAYS_DIFF_FOR_COMMENTS`],
  scripts_dir: dir,
  launch_benchmark_conf_file: dir + "launch_benchmark.conf",
  launch_benchmark_log_file: dir + "launch_benchmark.log",
  s3_workloads_script: dir + "s3workloads.sh",
  automate_passwordless_script: "automatePasswordless.sh"
};
