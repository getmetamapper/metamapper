import { graphql } from "react-apollo"
import { map } from "lodash"
import GetDatastoreAssets from "graphql/queries/GetDatastoreAssets"

const withGetDatastoreAssets = graphql(GetDatastoreAssets, {
  options: ({
    search,
    match: { params: { datastoreSlug } },
  }) => {
    return {
      fetchPolicy: "network-only",
      variables: { datastoreSlug, search },
    }
  },
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      assets: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { datastoreAssets, fetchMore } = data

    if (!datastoreAssets) {
      return res
    }

    const {
      pageInfo: { endCursor, hasNextPage },
      edges,
    } = datastoreAssets

    return {
      assets: map(edges, ({ node }) => node),
      hasNextPage,
      fetchNextPage: () =>
        fetchMore({
          variables: { after: endCursor },
          updateQuery: (previousResult, { fetchMoreResult }) => {
            const newEdges = fetchMoreResult.datastoreAssets.edges;
            const pageInfo = fetchMoreResult.datastoreAssets.pageInfo;

            return newEdges.length
              ? {
                  // Put the new comments at the end of the list and update `pageInfo`
                  // so we have the new `endCursor` and `hasNextPage` values
                  datastoreAssets: {
                    __typename: previousResult.datastoreAssets.__typename,
                    edges: [...previousResult.datastoreAssets.edges, ...newEdges],
                    pageInfo,
                  }
                }
              : previousResult;
          }
        })
    }
  },
})

export default withGetDatastoreAssets
