import { graphql } from "react-apollo"
import GetWorkspaceBySlug from "./queries/GetWorkspaceBySlug"

const withGetWorkspaceBySlug = graphql(GetWorkspaceBySlug, {
  options: ({
    match: {
      params: { workspaceSlug },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: {
      slug: workspaceSlug,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspace: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      workspace: data.workspaceBySlug,
    }
  },
})

export default withGetWorkspaceBySlug
