import { graphql } from "react-apollo"
import GetDatastoreSettings from "graphql/queries/GetDatastoreSettings"

const withGetDatastoreSettings = graphql(GetDatastoreSettings, {
  options: ({
    match: {
      params: { datastoreSlug },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: { datastoreSlug },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastore: {},
    }

    if (!data || data.loading || data.error) {
      console.log(res.loading)
      return res
    }

    return {
      datastore: data.datastoreBySlug,
    }
  },
})

export default withGetDatastoreSettings
