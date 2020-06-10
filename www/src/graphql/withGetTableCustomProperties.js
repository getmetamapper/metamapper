import { graphql } from "react-apollo"
import GetCustomProperties from "./queries/GetCustomProperties"

const withGetTableCustomProperties = graphql(GetCustomProperties, {
  skip: ({ tableDefinition }) =>
    !tableDefinition || !tableDefinition.hasOwnProperty("id"),
  options: ({ tableDefinition: { id: objectId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { objectId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      customProperties: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      customProperties: data.customProperties,
    }
  },
})

export default withGetTableCustomProperties
