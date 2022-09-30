import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCheckExecutions from "graphql/queries/GetCheckExecutions"

const withGetCheckExecutions = graphql(GetCheckExecutions, {
  skip: ({ check }) => !check.hasOwnProperty("id"),
  options: ({ check: { id: checkId }}) => ({
    fetchPolicy: "network-only",
    variables: { checkId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      checkExecutions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { checkExecutions } = data

    if (!checkExecutions || !checkExecutions.hasOwnProperty("edges")) {
      return res
    }

    return {
      checkExecutions: map(checkExecutions.edges, ({ node }) => node),
    }
  },
})

export default withGetCheckExecutions
