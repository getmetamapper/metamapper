import Workspaces from "pages/Workspaces/Workspaces"
import General from "pages/WorkspaceSettings/General"
import Users from "pages/WorkspaceSettings/Users"
import UserProfile from "pages/WorkspaceSettings/UserProfile"
import Authentication from "pages/WorkspaceSettings/Authentication"
import AuthenticationEditSaml from "pages/WorkspaceSettings/AuthenticationEditSaml"
import AuthenticationSetupOAuth2Github from "pages/WorkspaceSettings/AuthenticationSetupOAuth2Github"
import AuthenticationSetupOAuth2Google from "pages/WorkspaceSettings/AuthenticationSetupOAuth2Google"
import AuthenticationSetupSaml from "pages/WorkspaceSettings/AuthenticationSetupSaml"
import AuthenticationSetupRouting from "pages/WorkspaceSettings/AuthenticationSetupRouting"
import Groups from "pages/WorkspaceSettings/Groups"
import GroupProfile from "pages/WorkspaceSettings/GroupProfile"
import CustomFields from "pages/WorkspaceSettings/CustomFields"

export default [
  {
    component: Users,
    path: "/:workspaceSlug/settings/users",
    namespace: "workspace-users",
    exact: true,
  },
  {
    component: UserProfile,
    path: "/:workspaceSlug/settings/users/:userId",
    namespace: "workspace-users",
  },
  {
    component: AuthenticationSetupOAuth2Github,
    path: "/:workspaceSlug/settings/authentication/setup/github",
    namespace: "workspace-saml-setup",
  },
  {
    component: AuthenticationSetupOAuth2Google,
    path: "/:workspaceSlug/settings/authentication/setup/google",
    namespace: "workspace-saml-setup",
  },
  {
    component: AuthenticationSetupSaml,
    path: "/:workspaceSlug/settings/authentication/setup/generic",
    namespace: "workspace-saml-setup",
  },
  {
    component: AuthenticationEditSaml,
    path: "/:workspaceSlug/settings/authentication/:ssoPrimaryKey/edit",
    namespace: "workspace-saml-editing",
  },
  {
    component: AuthenticationSetupRouting,
    path: "/:workspaceSlug/settings/authentication/setup",
    namespace: "workspace-setup-routing",
  },
  {
    component: Authentication,
    path: "/:workspaceSlug/settings/authentication",
    namespace: "workspace",
  },
  {
    component: CustomFields,
    path: "/:workspaceSlug/settings/customproperties",
    namespace: "workspace",
  },
  {
    component: Groups,
    path: "/:workspaceSlug/settings/groups",
    namespace: "workspace",
    exact: true,
  },
  {
    component: GroupProfile,
    path: "/:workspaceSlug/settings/groups/:groupId",
    namespace: "groups",
  },
  {
    component: General,
    path: "/:workspaceSlug/settings",
    exact: true,
    namespace: "workspace",
  },
  {
    component: Workspaces,
    path: "/workspaces",
    exact: true,
    namespace: "workspaces",
    shouldRefreshUser: true,
  },
]
