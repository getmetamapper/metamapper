import { graphql } from "react-apollo"
import GetOmnisearchTags from "./queries/GetOmnisearchTags"

const withGetOmnisearchTags = graphql(GetOmnisearchTags, {
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      searchTags: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return {
      searchTags: data.omnisearchTags,
    }
  },
})

export default withGetOmnisearchTags
