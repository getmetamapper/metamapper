import gql from "graphql-tag"

export default gql`
  query GetCustomProperties($objectId: ID!) {
    customProperties(objectId: $objectId)
  }
`
