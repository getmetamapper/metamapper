import { graphql } from "react-apollo"
import { map } from "lodash"
import GetTableRevisions from "./queries/GetTableRevisions"

const withGetTableRevisions = graphql(GetTableRevisions, {
  skip: ({ tableDefinition }) =>
    !tableDefinition || !tableDefinition.hasOwnProperty("id"),
  options: ({ tableDefinition: { id: tableId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { tableId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      tableRevisions: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      tableRevisions: map(data.tableRevisions.edges, ({ node }) => node),
    }
  },
})

export default withGetTableRevisions
