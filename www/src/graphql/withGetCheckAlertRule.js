import { graphql } from "react-apollo"
import { b64encode } from "lib/utilities"
import GetCheckAlertRule from "graphql/queries/GetCheckAlertRule"

const withGetCheckAlertRule = graphql(GetCheckAlertRule, {
  options: ({
    match: {
      params: { ruleId },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: { id: b64encode(`CheckAlertRuleType:${ruleId}`) }
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      checkAlertRule: {},
    }

    console.log(res)

    if (!data || data.loading || data.error) {
      return res
    }

    return { checkAlertRule: data.checkAlertRule }
  },
})

export default withGetCheckAlertRule
