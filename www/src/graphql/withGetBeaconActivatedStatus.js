import { graphql } from "react-apollo"
import GetBeaconActivatedStatus from "graphql/queries/GetBeaconActivatedStatus"

const withGetBeaconActivatedStatus = graphql(GetBeaconActivatedStatus, {
  options: (props) => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      beaconActivated: null,
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetBeaconActivatedStatus
