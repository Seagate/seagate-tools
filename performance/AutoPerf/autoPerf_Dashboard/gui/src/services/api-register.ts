/*****************************************************************************
 Filename:          api-register.ts
 Description:       API Register: use for maintainging single registry for API

 Creation Date:     05/09/2019
 Author:            Shri Bhargav Metta

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 *****************************************************************************/
export const version = "v1.0";

export default {
  login: `api/${version}/user/login`,
  user_registration: `api/${version}/user/registration`,
  logout: `/api/${version}/logout`,
  default_parameters: `/api/${version}/metadata/default_parameters`,
  script_execution: `/api/${version}/script/executions`,
  components: `/api/${version}/component`,
  managers: `/api/${version}/manager`,
  metadata_node: `/api/${version}/metadata/node`,
  metadata_client: `/api/${version}/metadata/client`,
};
