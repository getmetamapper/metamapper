import { graphql } from "react-apollo"
import { map } from "lodash"
import GetApiTokens from "./queries/GetApiTokens"

const withGetApiTokens = graphql(GetApiTokens, {
  options: (props) => ({
    fetchPolicy: "network-only",
    variables: {},
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      apiTokens: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { apiTokens } = data

    if (!apiTokens || !apiTokens.hasOwnProperty("edges")) {
      return res
    }

    return {
      apiTokens: map(apiTokens.edges, ({ node }) => node),
    }
  },
})

export default withGetApiTokens
