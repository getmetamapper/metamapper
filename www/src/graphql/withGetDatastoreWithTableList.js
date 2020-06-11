import { graphql } from "react-apollo"
import GetDatastoreWithTableList from "graphql/queries/GetDatastoreWithTableList"

const withGetDatastoreWithTableList = graphql(GetDatastoreWithTableList, {
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

export default withGetDatastoreWithTableList
