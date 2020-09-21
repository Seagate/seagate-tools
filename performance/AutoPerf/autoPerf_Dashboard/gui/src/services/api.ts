/*****************************************************************************
 Filename:          api.ts
 Description:       API Service

 Creation Date:     05/09/2019
 Author:            Sanjeevan Bhave

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 *****************************************************************************/
import axios from "axios";
import router from "../router"; // Get router object from our router.ts
import { ApiResponse } from "./api-model";

// Add a request interceptor
// Set valid token into each request header
// Note: - if welcome page no need of auth token
//       - if create admin user page no need of auth token
axios.interceptors.request.use(
  (config) => {
    const constStr = require("../common/const-string.json");
    const token = localStorage.getItem(constStr.access_token);
    if (token) {
      config.headers.auth = token;
    }
    if (config.timeout === -1) {
      config.timeout = 0;
    } else if (config.timeout === 0) {
      config.timeout = 20000;
    }
    return config;
  },
  (error) => {
    Promise.reject(error);
  }
);

// Handle response
axios.interceptors.response.use(
  (response) => {
    if (response && response.data && response.data.statusCode === 401) {
      const constStr = require("../common/const-string.json");
      localStorage.removeItem(constStr.access_token);
      localStorage.removeItem(constStr.gid);
      router.push("/login");
    }
    return response;
  },
  (error) => {
    // Handle Unauthorised response. Re-route to login page if unauthorised response received.
    if (error.response && error.response.status === 401) {
      const constStr = require("../common/const-string.json");
      localStorage.removeItem(constStr.access_token);
      localStorage.removeItem(constStr.gid);
      router.push("/login");
    }
    return Promise.reject(error);
  }
);

export abstract class Api {
  // Wrapper method to for get api
  public static async getAll(
    url: string,
    queryParams?: object
  ): Promise<ApiResponse> {
    return await axios
      .get(url, { params: queryParams })
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }
  // Wrapper method to for get api
  public static async getFile(url: string, queryParams?: object) {
    return await axios.get(url, { responseType: "blob" });
  }
  // Wrapper method for update api
  public static async patch(
    url: string,
    payload: object,
    id?: string,
    config?: object
  ) {
    const tempURL = id ? url + "/" + id : url;
    return await axios
      .patch(tempURL, payload, config)
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }
  // Wrapper method for post api
  public static async post(url: string, payload: object, config?: object) {
    return await axios
      .post(url, payload, config)
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }
  // Wrapper method for post api to upload file
  public static async uploadFile(url: string, payload: FormData) {
    return await axios
      .post(url, payload, {
        headers: {
          "Content-Type": "multipart/form-data"
        },
        timeout: -1
      })
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }
  // Wrapper method for post api
  public static async delete(url: string, id: string) {
    const tempURL = id ? url + "/" + id : url;
    return await axios
      .delete(tempURL)
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }
  // Wrapper method for update api
  public static async put(
    url: string,
    payload: object,
    id: string,
    config?: object
  ) {
    const tempURL = id ? url + "/" + id : url;
    return await axios
      .put(tempURL, payload, config)
      .then((response) => {
        return Promise.resolve(this.buildSuccessResponse(response));
      })
      .catch((error) => {
        const apiResponse: ApiResponse = this.getResponseFromError(error);
        return Promise.reject(apiResponse);
      });
  }

  private static buildSuccessResponse(response: any): ApiResponse {
    const apiResponse: ApiResponse = {
      data: response.data,
      headers: response.headers,
      status: response.status,
      statusText: response.statusText
    };
    return apiResponse;
  }

  private static getResponseFromError(error: any): ApiResponse {
    let apiResponse: ApiResponse;
    if (error.code && error.code === "ECONNABORTED") {
      apiResponse = this.buildReqCancelledWarnResp(error);
    } else {
      apiResponse = this.buildErrorResponse(error.response);
    }
    return apiResponse;
  }

  private static buildErrorResponse(response: any): ApiResponse {
    const apiResponse: ApiResponse = {
      data: response.data ? response.data : {},
      status: response.status,
      statusText: response.statusText,
      error: {
        name: "Error: " + response.status,
        message: response.statusText
      }
    };
    return apiResponse;
  }

  private static buildReqCancelledWarnResp(error: any): ApiResponse {
    const apiResponse: ApiResponse = {
      status: error.code,
      statusText: error.message,
      warning: {
        message:
          "Server is taking too long to respond. Please refresh the page."
      }
    };
    return apiResponse;
  }
}
