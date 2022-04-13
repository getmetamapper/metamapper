import { graphql } from "react-apollo"
import GetCheckAlertRuleOptions from "graphql/queries/GetCheckAlertRuleOptions"

const withGetCheckAlertRuleOptions = graphql(GetCheckAlertRuleOptions, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      channelOptions: [],
      intervalOptions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetCheckAlertRuleOptions
