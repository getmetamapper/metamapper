import { graphql } from "react-apollo"
import qs from "query-string"
import GetOmnisearchResults from "./queries/GetOmnisearchResults"

const withGetOmnisearchResults = graphql(GetOmnisearchResults, {
  options: ({ location: { search } }) => {
    const { q: content } = qs.parse(search)

    let {
      datastores,
      types,
      engines,
      schemas,
      tags,
    } = qs.parse(search)

    if (datastores && !Array.isArray(datastores)) {
      datastores = [datastores]
    }

    if (types && !Array.isArray(types)) {
      types = [types]
    }

    if (engines && !Array.isArray(engines)) {
      engines = [engines]
    }

    if (schemas && !Array.isArray(schemas)) {
      schemas = [schemas]
    }

    if (tags && !Array.isArray(tags)) {
      tags = [tags]
    }

    return {
      fetchPolicy: "cache-first",
      variables: {
        content,
        datastores,
        types,
        engines,
        schemas,
        tags,
      },
    }
  },
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      facets: {},
      results: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data.omnisearch
  },
})

export default withGetOmnisearchResults
