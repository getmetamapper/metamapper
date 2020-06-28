import { graphql } from "react-apollo"
import { map } from "lodash"
import GetComments from "graphql/queries/GetComments"

const withGetObjectComments = graphql(GetComments, {
  skip: ({ contentObject }) => !contentObject.hasOwnProperty("id"),
  options: ({ contentObject: { id: objectId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: {
      objectId,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      comments: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { comments } = data

    if (!comments || !comments.hasOwnProperty("edges")) {
      return res
    }

    data.stopPolling()

    return {
      comments: map(comments.edges, ({ node }) => node),
    }
  },
})

export default withGetObjectComments
