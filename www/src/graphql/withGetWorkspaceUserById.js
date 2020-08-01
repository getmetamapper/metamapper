import { graphql } from "react-apollo"
import GetWorkspaceUser from "graphql/queries/GetWorkspaceUser"

const withGetWorkspaceUserById = graphql(GetWorkspaceUser, {
  options: ({ userId }) => ({
    fetchPolicy: "network-only",
    variables: { userId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspaceUser: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      workspaceUser: data.workspaceUser,
    }
  },
})

export default withGetWorkspaceUserById
