import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCustomFields from "./queries/GetCustomFields"

const withGetCustomDatastoreFields = graphql(GetCustomFields, {
  options: () => ({
    fetchPolicy: "network-only",
    variables: { contentType: "DATASTORE" },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      customDatastoreFields: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { customFields } = data

    return {
      customDatastoreFields: map(customFields.edges, ({ node }) => node),
    }
  },
})

export default withGetCustomDatastoreFields
