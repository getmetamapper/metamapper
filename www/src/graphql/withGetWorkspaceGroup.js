import { graphql } from "react-apollo"
import GetWorkspaceGroup from "graphql/queries/GetWorkspaceGroup"

const withGetWorkspaceGroup = graphql(GetWorkspaceGroup, {
  options: ({
    match: {
      params: { groupId },
    },
  }) => ({
    fetchPolicy: "cache-first",
    variables: { groupId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspaceGroup: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      workspaceGroup: data.workspaceGroup,
    }
  },
})

export default withGetWorkspaceGroup
