import React from "react"
import ReactDOM from "react-dom"
import { BrowserRouter as Router, Switch } from "react-router-dom"
import { ApolloProvider } from "react-apollo"
import { ApolloClient } from "apollo-client"
import { InMemoryCache } from "apollo-cache-inmemory"
import Route from "app/Navigation/Route"
import NotFound from "app/Errors/NotFound"
import WorkspaceRedirect from "pages/Workspaces/WorkspaceRedirect"
import hljs from "highlight.js"
import CodeMirror from "codemirror"
import ReactQuill from "react-quill"
import QuillMagicUrl from "quill-magic-url"
import QuillEmoji from "quill-emoji"

// eslint-disable-next-line
import "react-quill/dist/quill.core.css"
import "react-quill/dist/quill.snow.css"
import "quill-emoji/dist/quill-emoji.css"
import "highlight.js/styles/solarized-light.css"
import "codemirror/lib/codemirror.css"
import "codemirror/theme/base16-light.css"
import "codemirror/mode/markdown/markdown"
import "codemirror/mode/sql/sql"
import "./index.scss"

// eslint-disable-next-line
import i18n from "./i18n"
import * as serviceWorker from "./serviceWorker"
import link from "./lib/links"
import routes from "./routes"

window.hljs = hljs
window.CodeMirror = CodeMirror

ReactQuill.Quill.register('modules/magicUrl', QuillMagicUrl)
ReactQuill.Quill.register(
  {
    "formats/emoji": QuillEmoji.EmojiBlot,
    "modules/emoji-toolbar": QuillEmoji.ToolbarEmoji,
    "modules/emoji-textarea": QuillEmoji.TextAreaEmoji,
    "modules/emoji-shortname": QuillEmoji.ShortNameEmoji,
  },
  true,
)

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
