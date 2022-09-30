import { graphql } from "react-apollo"
import GetAvailableIntegrations from "graphql/queries/GetAvailableIntegrations"

const withGetAvailableIntegrations = graphql(GetAvailableIntegrations, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      availableIntegrations: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetAvailableIntegrations
