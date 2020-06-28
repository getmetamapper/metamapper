import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCustomFields from "./queries/GetCustomFields"

const withGetCustomFields = graphql(GetCustomFields, {
  options: ({ contentType }) => ({
    fetchPolicy: "network-only",
    variables: { contentType },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      customFields: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { customFields } = data

    if (!customFields || !customFields.hasOwnProperty("edges")) {
      return res
    }

    return {
      customFields: map(customFields.edges, ({ node }) => node),
    }
  },
})

export default withGetCustomFields
