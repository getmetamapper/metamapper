import { graphql } from "react-apollo"
import GetDatastoreIntervalOptions from "graphql/queries/GetDatastoreIntervalOptions"

const withGetDatastoreIntervalOptions = graphql(GetDatastoreIntervalOptions, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastoreIntervalOptions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetDatastoreIntervalOptions
