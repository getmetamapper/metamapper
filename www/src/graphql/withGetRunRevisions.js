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

    const { runRevisions, fetchMore } = data

    if (!runRevisions || !runRevisions.hasOwnProperty("edges")) {
      return res
    }

    data.stopPolling()

    const {
      pageInfo: { endCursor, hasNextPage },
      edges,
    } = runRevisions

    return {
      runRevisions: map(edges, ({ node }) => node),
      hasNextPage,
      refetch: data.refetch,
      fetchNextPage: () =>
        fetchMore({
          variables: { after: endCursor },
          updateQuery: (previousResult, { fetchMoreResult }) => {
            const newEdges = fetchMoreResult.runRevisions.edges;
            const pageInfo = fetchMoreResult.runRevisions.pageInfo;

            return newEdges.length
              ? {
                  // Put the new comments at the end of the list and update `pageInfo`
                  // so we have the new `endCursor` and `hasNextPage` values
                  runRevisions: {
                    __typename: previousResult.runRevisions.__typename,
                    edges: [...previousResult.runRevisions.edges, ...newEdges],
                    pageInfo,
                  }
                }
              : previousResult;
          }
        })
    }

  },
})

export default withGetRunRevisions
