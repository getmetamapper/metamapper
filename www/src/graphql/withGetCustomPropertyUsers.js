import { graphql } from "react-apollo"
import { map } from "lodash"
import GetWorkspaceUsers from "./queries/GetWorkspaceUsers"

const withGetCustomPropertyUsers = graphql(GetWorkspaceUsers, {
  options: ({ currentWorkspace: { id: workspaceId } }) => ({
    fetchPolicy: "cache-first",
    variables: {
      workspaceId,
      activeOnly: true,
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      users: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { workspaceUsers } = data

    if (!workspaceUsers || !workspaceUsers.hasOwnProperty("edges")) {
      return res
    }

    return {
      users: map(workspaceUsers.edges, ({ node }) => node),
    }
  },
})

export default withGetCustomPropertyUsers
