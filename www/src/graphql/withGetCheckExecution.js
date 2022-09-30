import { graphql } from "react-apollo"
import GetCheckExecution from "graphql/queries/GetCheckExecution"

const withGetCheckExecution = graphql(GetCheckExecution, {
  options: ({ checkExecution: { id } }) => ({
    fetchPolicy: "network-only",
    variables: { id }
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      checkExecution: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return { checkExecution: data.checkExecution }
  },
})

export default withGetCheckExecution
