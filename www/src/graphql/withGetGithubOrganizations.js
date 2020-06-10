import { graphql } from "react-apollo"
import GetGithubOrganizations from "./queries/GetGithubOrganizations"

const withGetGithubOrganizations = graphql(GetGithubOrganizations, {
  options: () => ({
    fetchPolicy: "network-only",
    variables: {},
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      githubOrganizations: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    return data
  },
})

export default withGetGithubOrganizations
