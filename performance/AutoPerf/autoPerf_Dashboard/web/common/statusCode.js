/**
 * 1xx: Informational	Communicates transfer protocol-level information.
 * 2xx: Success	Indicates that the client’s request was accepted successfully.
 * 3xx: Redirection	Indicates that the client must take some additional action in order to complete their request.
 * 4xx: Client Error	This category of error status codes points the finger at clients.
 * 5xx: Server Error	The server takes responsibility for these error status codes.
 */

module.exports = {
  success: 200,
  created: 201,
  accepted: 202,
  no_content: 204,
  moved_permanently: 301,
  found: 302,
  see_others: 303,
  not_modifies: 304,
  temporary_redirect: 307,
  bad_request: 400,
  unauthorized: 401,
  forbidden: 403,
  not_found: 404,
  method_not_allowed: 405,
  not_acceptable: 406,
  precondition_failed: 412,
  unsupported_media_type: 415,
  internal_server_error: 500,
  not_implemented: 501,
  connection_failed: 503,
};
