import { graphql } from "react-apollo"
import qs from "query-string"
import GetOmnisearchResults from "./queries/GetOmnisearchResults"

const withGetOmnisearchResults = graphql(GetOmnisearchResults, {
  options: ({ location: { search } }) => {
    const { q: content, d: datastoreId } = qs.parse(search)
    return {
      fetchPolicy: "cache-first",
      variables: {
        content,
        datastoreId,
      },
    }
  },
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      searchResults: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data.omnisearch
  },
})

export default withGetOmnisearchResults
