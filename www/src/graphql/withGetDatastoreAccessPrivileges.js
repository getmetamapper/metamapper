import { graphql } from "react-apollo"
import GetDatastoreAccessPrivileges from "graphql/queries/GetDatastoreAccessPrivileges"

const withGetDatastoreAccessPrivileges = graphql(GetDatastoreAccessPrivileges, {
  skip: ({ datastore }) => !datastore || !datastore.hasOwnProperty("id"),
  options: ({ datastore: { id: datastoreId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { datastoreId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastoreUsers: [],
      datastoreGroups: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const {
      datastoreGroupAccessPrivileges,
      datastoreUserAccessPrivileges,
    } = data

    if (!datastoreGroupAccessPrivileges || !datastoreUserAccessPrivileges) {
      return res
    }

    data.stopPolling()

    return {
      datastoreGroups: datastoreGroupAccessPrivileges,
      datastoreUsers: datastoreUserAccessPrivileges,
      nonce: Math.random(),
    }
  },
})

export default withGetDatastoreAccessPrivileges
