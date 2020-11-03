import { graphql } from "react-apollo"
import { find, map } from "lodash"
import GetDatastoreFacet from "graphql/queries/GetDatastoreFacet"

const withGetDatastoreFacet = graphql(GetDatastoreFacet, {
  options: () => ({ fetchPolicy: "network-only" }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      datastores: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const {
      datastores: rawDatastores,
      datastoreEngines,
    } = data

    if (!rawDatastores || !rawDatastores.hasOwnProperty("edges")) {
      return res
    }

    const datastores = map(rawDatastores.edges, ({ node }) => {
      const engine = find(datastoreEngines, ({ dialect }) => dialect === node.jdbcConnection.engine)
      node.engineName = engine.label
      return node
    })

    return {
      datastores,
    }
  },
})

export default withGetDatastoreFacet
