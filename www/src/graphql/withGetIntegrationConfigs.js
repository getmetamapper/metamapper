import { graphql } from "react-apollo"
import { map } from "lodash"
import GetIntegrationConfigs from "graphql/queries/GetIntegrationConfigs"

const withGetIntegrationConfigs = graphql(GetIntegrationConfigs, {
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
      integrationConfigs: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { integration, integrationConfigs } = data

    return {
      integration,
      integrationConfigs: map(integrationConfigs.edges, ({ node }) => node),
    }
  },
})

export default withGetIntegrationConfigs
