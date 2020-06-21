import { graphql } from "react-apollo"
import GetDatastoreCount from "graphql/queries/GetDatastoreCount"

const withGetDatastoreCount = graphql(GetDatastoreCount, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastoreCount: -1,
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return { datastoreCount: data.datastores.totalCount }
  },
})

export default withGetDatastoreCount
