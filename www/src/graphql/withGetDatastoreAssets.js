import { graphql } from "react-apollo"
import GetDatastoreAssets from "graphql/queries/GetDatastoreAssets"

const withGetDatastoreAssets = graphql(GetDatastoreAssets, {
  options: ({
    match: {
      params: { datastoreSlug },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: {
      datastoreSlug,
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastore: {},
      schemas: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { datastoreBySlug } = data

    if (!datastoreBySlug) {
      return res
    }

    return {
      datastore: datastoreBySlug,
      schemas: datastoreBySlug.schemas,
    }
  },
})

export default withGetDatastoreAssets
