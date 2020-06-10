export const AUTH_TOKEN = "auth-token"
export const WORKSPACE_TOKEN = "workspace-token"
export const REDIRECT_URI = "redirect-uri"
export const WORKSPACE_ID = "workspace-id"
export const PASSWORD_STRENGTH = 2
export const JWT_EXPIRATION_DELTA = 5 * 60 * 1000 // 5 minutes
export const JWT_REFRESH_EXPIRATION_DELTA = 3 * 24 * 60 * 60 * 1000 // 3 days
export const DEFAULT_PERMISSION = "MEMBER"
export const PERMISSION_CHOICES = {
  READONLY: "Readonly",
  MEMBER: "Member",
  OWNER: "Owner",
}
export const ORIGIN_HOST =
  window.location.hostname === "localhost"
    ? "http://localhost:5050"
    : window.location.origin
export const GITHUB_OAUTH2_CLIENT_ID = "3b9267cdfdc22a9776d7"
export const GOOGLE_OAUTH2_CLIENT_ID =
  "152652839171-k0u7lr2ckq84b2a4bsbde5rvcd52kni2.apps.googleusercontent.com"
