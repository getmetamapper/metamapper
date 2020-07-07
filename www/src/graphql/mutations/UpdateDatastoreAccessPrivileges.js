import gql from "graphql-tag"

export const queryAsString = `
  mutation UpdateDatastoreAccessPrivileges($id: ID!, $objectId: ID!, $privileges: [String]!) {
    updateDatastoreAccessPrivileges(input: {
      id: $id,
      objectId: $objectId,
      privileges: $privileges,
    }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`

export default gql(queryAsString)
