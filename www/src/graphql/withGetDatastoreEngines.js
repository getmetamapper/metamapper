import { graphql } from "react-apollo"
import GetDatastoreEngines from "graphql/queries/GetDatastoreEngines"

const withGetDatastoreEngines = graphql(GetDatastoreEngines, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastoreEngines: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetDatastoreEngines
