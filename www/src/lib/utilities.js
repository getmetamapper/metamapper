import React from "react"
import { message } from "antd"
import { AUTH_TOKEN, REDIRECT_URI } from "lib/constants"

export const isObject = (val) => {
  return typeof val === "object" && val !== null
}

export const isEmail = (email) => {
  return /^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$/.test( email );
}

export const isMobileDevice = () => {
  return (
    typeof window.orientation !== "undefined" ||
    navigator.userAgent.indexOf("IEMobile") !== -1 ||
    window.innerWidth < 700
  )
}

export const memoize = (method) => {
  let cache = {};

  return async function() {
    let args = JSON.stringify(arguments);
    cache[args] = cache[args] || method.apply(this, arguments);
    return cache[args];
  };
}

export let getErrorDefinition = memoize(async function(locale) {
  const res = await fetch(`/assets/locales/${locale}.yml`)
  const txt = await res.text()
  return txt
})

export const linkDecorator = (href, text, key) => (
  <a href={href} key={key} target="_blank" rel="noopener noreferrer">
    {text}
  </a>
)

export const humanize = (str) => {
  return str
    .trim()
    .split(/\s+/)
    .map(function (str) {
      return str.replace(/_/g, " ").replace(/\s+/, " ").trim()
    })
    .join(" ")
    .toLowerCase()
    .replace(/^./, function (m) {
      return m.toUpperCase()
    })
}

export const coalesce = (one, two) => {
  if (typeof one === "string") {
    one = one.trim()
  }
  return one || two
}

export const b64decode = (encodedMessage) => {
  try {
    return window.atob(encodedMessage)
  } catch (e) {
    return ""
  }
}

export const copyToClipboard = (str) => {
  const el = document.createElement("textarea")
  el.value = str
  document.body.appendChild(el)
  el.select()
  document.execCommand("copy")
  document.body.removeChild(el)
  message.success("Copied to clipboard.")
}

export const classnames = (...args) => {
  const classes = []
  args.forEach((arg) => {
    if (typeof arg === "string") {
      classes.push(arg)
    } else if (isObject(arg)) {
      Object.keys(arg).forEach((key) => {
        if (arg[key]) {
          classes.push(key)
        }
      })
    } else {
      throw new Error("`classnames` only accepts string or object as arguments")
    }
  })

  return classes.join(" ")
}

export const setToken = (token) => {
  window.localStorage.setItem(AUTH_TOKEN, token)
}

export const setTokenAndGetRedirectUri = (token, unset = false) => {
  const redirect_uri = window.localStorage.getItem(REDIRECT_URI)
  const redirect_url = redirect_uri ? decodeURIComponent(redirect_uri) : "/"

  setToken(token)

  if (unset) {
    window.localStorage.removeItem(REDIRECT_URI)
  }

  return redirect_url
}
