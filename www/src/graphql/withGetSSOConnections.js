import { graphql } from "react-apollo"
import { map } from "lodash"
import GetSSOConnections from "./queries/GetSSOConnections"

const withGetSSOConnections = graphql(GetSSOConnections, {
  options: (props) => ({
    fetchPolicy: "network-only",
    variables: {},
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      ssoConnections: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { ssoConnections } = data

    if (!ssoConnections || !ssoConnections.hasOwnProperty("edges")) {
      return res
    }

    return {
      ssoConnections: map(ssoConnections.edges, ({ node }) => node),
    }
  },
})

export default withGetSSOConnections
