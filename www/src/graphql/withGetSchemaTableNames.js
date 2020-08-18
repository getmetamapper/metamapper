import { graphql } from "react-apollo"
import GetSchemaTableNames from "graphql/queries/GetSchemaTableNames"

const withGetSchemaTableNames = graphql(GetSchemaTableNames, {
  options: ({
    datastore: { id: datastoreId },
    schemaName,
  }) => ({
    fetchPolicy: "cache-first",
    variables: {
      datastoreId,
      schemaName,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      schemaTableNames: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      schemaTableNames: data.tableNamesBySchema,
    }
  },
})

export default withGetSchemaTableNames
