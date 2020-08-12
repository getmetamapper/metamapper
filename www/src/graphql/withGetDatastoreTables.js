import { graphql } from "react-apollo"
import GetDatastoreTables from "graphql/queries/GetDatastoreTables"

const withGetDatastoreTables = graphql(GetDatastoreTables, {
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

export default withGetDatastoreTables
