import { ApolloLink } from "apollo-link"
import { setContext } from "apollo-link-context"
import { onError } from "apollo-link-error"
import { RetryLink } from "apollo-link-retry"
import jwtDecode from "jwt-decode"
import { createUploadLink } from "apollo-upload-client"
import { AUTH_TOKEN, WORKSPACE_TOKEN, ORIGIN_HOST } from "./constants"

const authLink = setContext((_, { headers }) => {
  // get the authentication token from local storage if it exists
  const token = localStorage.getItem(AUTH_TOKEN)

  if (token) {
    const decoded = jwtDecode(token)
    const currentTime = parseInt(Date.now().valueOf() / 1000)

    if (currentTime > decoded.exp) {
      localStorage.removeItem(AUTH_TOKEN)
      localStorage.removeItem(WORKSPACE_TOKEN)
    }
  }

  // return the headers to the context so httpLink can read them
  const config = {
    headers: {
      ...headers,
      Authorization: token ? `Bearer ${token}` : "",
    },
  }

  const workspace = localStorage.getItem(WORKSPACE_TOKEN)

  if (workspace) {
    config.headers["X-Workspace-Id"] = workspace
  }

  return config
})

const errorLink = onError(({ graphQLErrors, networkError }) => {
  // if (graphQLErrors)
  //   graphQLErrors.forEach(({ message, locations, path }) =>
  //     console.log(
  //       `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
  //     )
  //   );
  if (networkError) console.log(`[Network error]: ${networkError}`);
})

const doNotRetry = ['testJdbcConnection']

const retryLink = new RetryLink({
  attempts: (count, operation, error) => {
    return !!error && doNotRetry.indexOf(operation.operationName) > -1;
  },
  delay: {
    initial: 300,
    max: Infinity,
    jitter: true
  },
});

const link = ApolloLink.from([
  retryLink,
  errorLink,
  authLink,
  createUploadLink({ uri: `${ORIGIN_HOST}/graphql` }),
])

export default link
