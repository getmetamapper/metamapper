import LoginPrompt from "pages/Authentication/LoginPrompt"
import LoginWithToken from "pages/Authentication/LoginWithToken"
import Login from "pages/Authentication/Login"
import SingleSignOn from "pages/Authentication/SingleSignOn"
import SingleSignOnRedirect from "pages/Authentication/SingleSignOnRedirect"
import Signup from "pages/Authentication/Signup"
import PasswordReset from "pages/Authentication/PasswordReset"
import PasswordConfirm from "pages/Authentication/PasswordConfirm"
import Logout from "pages/Authentication/Logout"

export default [
  {
    component: SingleSignOnRedirect,
    path: "/login/sso/:workspaceSlug",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: SingleSignOn,
    path: "/login/sso",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: LoginWithToken,
    path: "/:workspaceSlug/sso/:uid/:singleUseToken",
    namespace: "authentication",
    isPublic: true,
    ignoreRedirects: true,
  },
  {
    component: Login,
    path: "/login/email",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: LoginPrompt,
    path: "/login",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: Signup,
    path: "/signup",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: PasswordReset,
    path: "/password/reset",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: PasswordConfirm,
    path: "/password/confirm/:uid/:token",
    namespace: "authentication",
    isProtected: false,
    isPublic: true,
  },
  {
    component: Logout,
    path: "/logout",
    namespace: "authentication",
    isProtected: true,
    isPublic: true,
  },
]
