import gql from "graphql-tag"

export default gql`
  query getCustomProperties($objectId: ID!) {
    customProperties(objectId: $objectId)
  }
`
