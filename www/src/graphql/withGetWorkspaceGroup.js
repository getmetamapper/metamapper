import { graphql } from "react-apollo"
import GetWorkspaceGroup from "graphql/queries/GetWorkspaceGroup"

const withGetWorkspaceGroup = graphql(GetWorkspaceGroup, {
  skip: ({ group }) => !group.hasOwnProperty("id"),
  options: ({ group: { id: groupId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
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

    data.stopPolling()

    return {
      workspaceGroup: data.workspaceGroup,
    }
  },
})

export default withGetWorkspaceGroup
