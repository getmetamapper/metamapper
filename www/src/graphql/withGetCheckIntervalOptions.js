import { graphql } from "react-apollo"
import GetCheckIntervalOptions from "graphql/queries/GetCheckIntervalOptions"

const withGetCheckIntervalOptions = graphql(GetCheckIntervalOptions, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      checkIntervalOptions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetCheckIntervalOptions
