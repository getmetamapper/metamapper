import { graphql } from "react-apollo"
import { map } from "lodash"
import GetWorkspaceGroupUsers from "./queries/GetWorkspaceGroupUsers"

const withGetWorkspaceGroupUsers = graphql(GetWorkspaceGroupUsers, {
  skip: ({ group }) => !group.hasOwnProperty("id"),
  options: ({ group: { id: groupId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { groupId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspaceGroupUsers: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { workspaceGroupUsers } = data

    if (!workspaceGroupUsers || !workspaceGroupUsers.hasOwnProperty("edges")) {
      return res
    }

    data.stopPolling()

    return {
      workspaceGroupUsers: map(workspaceGroupUsers.edges, ({ node }) => node),
    }
  },
})

export default withGetWorkspaceGroupUsers
