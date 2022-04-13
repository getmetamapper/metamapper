import { graphql } from "react-apollo"
import GetDatastoreCheck from "graphql/queries/GetDatastoreCheck"
import { b64encode } from "lib/utilities"

const withGetDatastoreCheck = graphql(GetDatastoreCheck, {
  options: ({
    match: {
      params: { checkId },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: {
      checkId: b64encode(`CheckType:${checkId}`)
    },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      check: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return { check: data.datastoreCheck }
  },
})

export default withGetDatastoreCheck
