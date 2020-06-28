import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCustomFields from "./queries/GetCustomFields"

const withGetCustomTableFields = graphql(GetCustomFields, {
  options: () => ({
    fetchPolicy: "network-only",
    variables: { contentType: "TABLE" },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      customTableFields: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { customFields } = data

    if (!customFields || !customFields.hasOwnProperty("edges")) {
      return res
    }

    return {
      customTableFields: map(customFields.edges, ({ node }) => node),
    }
  },
})

export default withGetCustomTableFields
