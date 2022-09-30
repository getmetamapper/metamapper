import { graphql } from "react-apollo"
import { map } from "lodash"
import GetCheckAlertRules from "graphql/queries/GetCheckAlertRules"

const withGetCheckAlertRules = graphql(GetCheckAlertRules, {
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
      checkAlertRules: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { checkAlertRules } = data

    if (!checkAlertRules || !checkAlertRules.hasOwnProperty("edges")) {
      return res
    }

    return {
      checkAlertRules: map(checkAlertRules.edges, ({ node }) => node),
    }
  },
})

export default withGetCheckAlertRules
