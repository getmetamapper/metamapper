import { graphql } from "react-apollo"
import { map } from "lodash"
import GetSSODomains from "./queries/GetSSODomains"

const withGetSSODomains = graphql(GetSSODomains, {
  options: (props) => ({
    fetchPolicy: "network-only",
    variables: {},
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      ssoDomains: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { ssoDomains } = data

    return {
      ssoDomains: map(ssoDomains.edges, ({ node }) => node),
    }
  },
})

export default withGetSSODomains
