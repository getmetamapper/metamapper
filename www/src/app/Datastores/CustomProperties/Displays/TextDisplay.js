import React from "react"
import Interweave from "interweave"
import { UrlMatcher } from "interweave-autolink"
import { MarkdownUrlMatcher } from "lib/interweave-matchers"

const TextDisplay = ({ value }) => (
  <Interweave
    content={value}
    noHtmlExceptMatchers
    newWindow
    matchers={[
      new MarkdownUrlMatcher('markdownUrl'),
      new UrlMatcher('url'),
    ]}
  />
)

export default TextDisplay
