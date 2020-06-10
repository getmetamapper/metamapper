import { graphql } from "react-apollo"
import GetCustomProperties from "./queries/GetCustomProperties"

const withGetDatastoreCustomProperties = graphql(GetCustomProperties, {
  skip: ({ datastore }) => !datastore || !datastore.hasOwnProperty("id"),
  options: ({ datastore: { id: objectId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { objectId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      customProperties: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      customProperties: data.customProperties,
    }
  },
})

export default withGetDatastoreCustomProperties
