import { graphql } from "react-apollo"
import GetDatastoreSchemaNames from "graphql/queries/GetDatastoreSchemaNames"

const withGetDatastoreSchemaNames = graphql(GetDatastoreSchemaNames, {
  options: ({
    datastore: { id: datastoreId },
  }) => ({
    fetchPolicy: "cache-first",
    variables: {
      datastoreId,
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastoreSchemaNames: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      datastoreSchemaNames: data.schemaNamesByDatastore,
    }
  },
})

export default withGetDatastoreSchemaNames
