import React from "react"
import Interweave from "interweave"
import { UrlMatcher } from "interweave-autolink";


const TextDisplay = ({ value }) => <Interweave content={value} noHtmlExceptMatchers matchers={[new UrlMatcher('url')]} />

export default TextDisplay
