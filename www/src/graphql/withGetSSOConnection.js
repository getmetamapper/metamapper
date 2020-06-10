import { graphql } from "react-apollo"
import GetSSOConnection from "./queries/GetSSOConnection"

const withGetSSOConnection = graphql(GetSSOConnection, {
  options: ({
    match: {
      params: { ssoPrimaryKey },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: { pk: ssoPrimaryKey },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      ssoConnection: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      ssoConnection: data.ssoConnectionByPrimaryKey,
    }
  },
})

export default withGetSSOConnection
