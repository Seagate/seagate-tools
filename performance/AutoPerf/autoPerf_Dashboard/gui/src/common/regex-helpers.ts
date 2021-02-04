import { helpers } from "vuelidate/lib/validators";
export const accountNameRegex = helpers.regex(
  "accountNameRegex",
  /^[a-zA-Z0-9_-]{4,56}$/
);
export const accountNameTooltipMessage =
  // tslint:disable-next-line: max-line-length
  "The account name must be of minimum 4 characters and maximum 56 characters. The username must be alphanumeric and can contain underscore (_) and dash (-).";

export const usernameTooltipMessage =
  // tslint:disable-next-line
  "The username must be of minimum 4 characters and maximum 56 characters. The username must be alphanumeric and can contain underscore (_) and dash (-).";

export const bucketNameRegex = helpers.regex(
  "bucketNameRegex",
  /^[a-z0-9][a-z0-9-]{3,54}[a-z0-9]$/
);
export const bucketNameTooltipMessage = `The bucket name must be of minimum 4 characters and maximum 56 characters.
Only lowercase, numbers, and dash (-) are allowed. The bucket name cannot start and end with a dash (-).`;

export const passwordRegex = helpers.regex(
  "passwordRegex",
  // tslint:disable-next-line
  /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#\$%\^&\*\(\)\_\+\-\=\[\]\{\}\|\'])[A-Za-z\d!@#\$%\^&\*\(\)\_\+\-\=\[\]\{\}\|\']{8,}/
);
export const passwordTooltipMessage =
  // tslint:disable-next-line
  "Password must contain: Minimum 8 characters, One uppercase letter, One lowercase letter, One special character, One number";

export const iamPathRegex = helpers.regex("pathRegex", /^(\/[^/ ]*)+\/?$/);
// tslint:disable-next-line
export const commaSeparatedEmailsRegex = helpers.regex(
  "commaSeparatedEmailsRegex",
  /^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$/
);

export const udxBucketNameRegex = helpers.regex(
  "udxBucketNameRegex",
  /^[a-z0-9-]{0,51}[a-z0-9]$/
);
export const udxBucketNameTooltipMessage = `The bucket name must be of minimum 5 characters and maximum 56 characters.
  Only lowercase, numbers, and dash (-) are allowed. The bucket name cannot start and end with a dash (-).`;

export const udxURLRegex = helpers.regex(
  "udxURLRegex",
  /^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/
);
