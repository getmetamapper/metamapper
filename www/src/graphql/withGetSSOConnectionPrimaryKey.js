import { graphql } from "react-apollo"
import GetSSOConnectionPrimaryKey from "./queries/GetSSOConnectionPrimaryKey"

const withGetSSOConnectionPrimaryKey = graphql(GetSSOConnectionPrimaryKey, {
  options: (props) => ({
    fetchPolicy: "network-only",
    variables: {},
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      ssoPrimaryKey: null,
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      ssoPrimaryKey: data.ssoPrimaryKey,
    }
  },
})

export default withGetSSOConnectionPrimaryKey
