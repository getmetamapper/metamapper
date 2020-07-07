import gql from "graphql-tag"

export default gql`
  query GetDatastoreAccessPrivileges($datastoreId: ID!) {
    datastoreUserAccessPrivileges(datastoreId: $datastoreId) {
      id
      name
      privileges
    }
    datastoreGroupAccessPrivileges(datastoreId: $datastoreId) {
      id
      name
      privileges
    }
  }
`
