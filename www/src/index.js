import React from "react"
import ReactDOM from "react-dom"
import { BrowserRouter as Router, Switch } from "react-router-dom"
import { ApolloProvider } from "react-apollo"
import { ApolloClient } from "apollo-client"
import { InMemoryCache } from "apollo-cache-inmemory"
import Route from "app/Navigation/Route"
import NotFound from "app/Errors/NotFound"
import WorkspaceRedirect from "pages/Workspaces/WorkspaceRedirect"
import trix from "trix" /* eslint-disable no-unused-vars */

import "./index.scss"
import * as serviceWorker from "./serviceWorker"
import link from "./lib/links"
import routes from "./routes"


const client = new ApolloClient({
  link,
  cache: new InMemoryCache(),
  fetchOptions: {
    mode: "no-cors",
  },
})

const App = () => (
  <ApolloProvider client={client}>
    <Router>
      <section>
        <Switch>
          {routes.map((properties, index) => (
            <Route key={index} {...properties} />
          ))}
          <Route isPublic path="/" exact component={WorkspaceRedirect} />
          <Route isPublic path="*" exact={true} component={NotFound} />
        </Switch>
      </section>
    </Router>
  </ApolloProvider>
)

ReactDOM.render(<App />, document.getElementById("root"))

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister()
