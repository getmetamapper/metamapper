import { graphql } from "react-apollo"
import { map } from "lodash"
import GetDatastoreChecks from "graphql/queries/GetDatastoreChecks"

const withGetDatastoreChecks = graphql(GetDatastoreChecks, {
  skip: ({ datastore }) => !datastore.hasOwnProperty("id"),
  options: ({ datastore: { id: datastoreId } }) => ({
    fetchPolicy: "network-only",
    variables: {
      datastoreId,
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      checks: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { datastoreChecks } = data

    if (!datastoreChecks || !datastoreChecks.hasOwnProperty("edges")) {
      return res
    }

    return {
      checks: map(datastoreChecks.edges, ({ node }) => node),
      loading: false,
    }
  },
})

export default withGetDatastoreChecks
