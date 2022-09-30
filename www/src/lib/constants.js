export const AUTH_TOKEN = "auth-token"
export const WORKSPACE_TOKEN = "workspace-token"
export const REDIRECT_URI = "redirect-uri"
export const USER_ID = "user-id"
export const WORKSPACE_ID = "workspace-id"
export const PASSWORD_STRENGTH = 2
export const JWT_EXPIRATION_DELTA = 5 * 60 * 1000 // 5 minutes
export const JWT_REFRESH_EXPIRATION_DELTA = 3 * 24 * 60 * 60 * 1000 // 3 days
export const DEFAULT_PERMISSION = "MEMBER"
export const TIMESTAMP_FORMAT = "MMMM Do, YYYY [at] h:mma"
export const PERMISSION_CHOICES = {
  READONLY: "Readonly",
  MEMBER: "Member",
  OWNER: "Owner",
}
export const ORIGIN_HOST =
  process.env.NODE_ENV === "development"
    ? "http://localhost:5050"
    : window.location.origin
