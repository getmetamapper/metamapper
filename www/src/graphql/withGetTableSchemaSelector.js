import { graphql } from "react-apollo"
import GetTableSchemaSelector from "graphql/queries/GetTableSchemaSelector"

const withGetTableSchemaSelector = graphql(GetTableSchemaSelector, {
  options: ({
    match: {
      params: { datastoreSlug },
    },
  }) => ({
    fetchPolicy: "no-cache",
    variables: {
      datastoreSlug,
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
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
      schemas: datastoreBySlug.schemas,
    }
  },
})

export default withGetTableSchemaSelector
