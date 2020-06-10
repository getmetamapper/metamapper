import { graphql } from "react-apollo"
import { map } from "lodash"
import GetRunRevisions from "./queries/GetRunRevisions"

const withGetRunRevisions = graphql(GetRunRevisions, {
  skip: ({ run }) => !run || !run.hasOwnProperty("id"),
  options: ({ run: { id: runId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { runId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      runRevisions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      runRevisions: map(data.runRevisions.edges, ({ node }) => node),
    }
  },
})

export default withGetRunRevisions
