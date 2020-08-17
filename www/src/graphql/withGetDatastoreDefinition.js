import { graphql } from "react-apollo"
import GetDatastoreDefinition from "graphql/queries/GetDatastoreDefinitionBySlug"

const withGetDatastoreDefinition = graphql(GetDatastoreDefinition, {
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
      return res
    }

    return {
      datastore: data.datastoreBySlug,
    }
  },
})

export default withGetDatastoreDefinition
