import gql from "graphql-tag"

export default gql`
  mutation TriggerSingleSignOn($workspaceSlug: String!) {
    triggerSingleSignOn(workspaceSlug: $workspaceSlug) {
      redirectUrl
    }
  }
`
