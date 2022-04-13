import { graphql } from "react-apollo"
import GetCheckHandlerOptions from "graphql/queries/GetCheckHandlerOptions"

const withGetCheckHandlerOptions = graphql(GetCheckHandlerOptions, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      expectationHandlers: [],
      passValueHandlers: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetCheckHandlerOptions
