import { graphql } from "react-apollo"
import GetIntegration from "graphql/queries/GetIntegration"

const withGetIntegration = graphql(GetIntegration, {
  options: ({
    match: {
      params: { integration },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: {
      id: integration.toUpperCase(),
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      integration: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetIntegration
