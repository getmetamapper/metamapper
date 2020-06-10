import { graphql } from "react-apollo"
import { orderBy } from "lodash"
import GetSSOProviders from "graphql/queries/GetSSOProviders"

const withGetSSOProviders = graphql(GetSSOProviders, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      ssoProviders: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      ssoProviders: orderBy(data.ssoProviders, "protocol"),
    }
  },
})

export default withGetSSOProviders
