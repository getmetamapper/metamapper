import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCheckExpectations from "graphql/queries/GetCheckExpectations"

const withGetCheckExpectations = graphql(GetCheckExpectations, {
  skip: ({ check }) => !check || !check.hasOwnProperty("id"),
  options: ({ check: { id: checkId }}) => ({
    fetchPolicy: "network-only",
    variables: { checkId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      expectations: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { checkExpectations } = data

    if (!checkExpectations || !checkExpectations.hasOwnProperty("edges")) {
      return res
    }

    return {
      expectations: map(checkExpectations.edges, ({ node }) => node),
    }
  },
})

export default withGetCheckExpectations
