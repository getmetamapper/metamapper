import { graphql } from "react-apollo"
import { map } from "lodash"
import qs from "query-string"
import GetDatastores from "graphql/queries/GetDatastores"

const withGetDatastoresList = graphql(GetDatastores, {
  options: ({ location: { search: sqs } }) => {
    const { search } = qs.parse(sqs)
    return {
      fetchPolicy: "network-only",
      variables: { search },
    }
  },
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastores: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { datastores } = data

    if (!datastores || !datastores.hasOwnProperty("edges")) {
      return res
    }

    return {
      loading: false,
      datastores: map(datastores.edges, ({ node }) => node),
    }
  },
})

export default withGetDatastoresList
