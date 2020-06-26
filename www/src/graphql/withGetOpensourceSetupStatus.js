import { graphql } from "react-apollo"
import GetOpensourceSetupStatus from "graphql/queries/GetOpensourceSetupStatus"

const withGetOpensourceSetupStatus = graphql(GetOpensourceSetupStatus, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      initiateSetupProcess: null,
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetOpensourceSetupStatus
