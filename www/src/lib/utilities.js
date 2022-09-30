import React from "react"
import { message } from "antd"
import { AUTH_TOKEN, REDIRECT_URI } from "lib/constants"

export const isObject = (val) => {
  return typeof val === "object" && val !== null
}

export const isEmail = (email) => {
  // eslint-disable-next-line
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

export const capitalize = (s) => {
  if (typeof s !== 'string') return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export let getErrorDefinition = memoize(async function(locale) {
  const res = await fetch(`/assets/locales/${locale}/errors.yml`)
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

export const ellipsis = (value, length = 40) => {
  if (value.length <= length) {
    return value
  }

  return `${value.substring(0, length - 1)}...`
}

export const coalesce = (one, two) => {
  if (typeof one === "string") {
    one = one.trim()
  }
  return one || two
}

export const b64encode = (message) => {
  try {
    return window.btoa(message)
  } catch (e) {
    return ""
  }
}

export const b64decode = (encodedMessage) => {
  try {
    return window.atob(encodedMessage)
  } catch (e) {
    return ""
  }
}

export const tryGetValue = (data, key) => {
  try {
    return data[key]
  } catch (e) {
    return null;
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

export const setTokenAndGetRedirectUri = (token, defaultPath) => {
  setToken(token)
  return parseRedirectUri(getWithExpiry(REDIRECT_URI), defaultPath)
}

export const parseRedirectUri = (next, defaultPath = "/") => {
  if (next) {
    const { origin } = parseURL(next)

    if (origin && origin === window.location.origin) {
      return next
    }
  }

  return defaultPath
}

export const parseURL = (string) => {
  try {
    return new URL(string);
  } catch (_) {
    return {};
  }
}

export const setWithExpiry = (key, value, ttl) => {
  const now = new Date()

  // `item` is an object which contains the original value
  // as well as the time when it's supposed to expire
  const item = {
    value: value,
    expiry: now.getTime() + ttl,
  }
  localStorage.setItem(key, JSON.stringify(item))
}

export const getWithExpiry = (key) => {
  const itemStr = localStorage.getItem(key)
  // if the item doesn't exist, return null
  if (!itemStr) {
    return null
  }
  const item = JSON.parse(itemStr)
  const now = new Date()
  // compare the expiry time of the item with the current time
  if (now.getTime() > item.expiry) {
    // If the item is expired, delete the item from storage
    // and return null
    localStorage.removeItem(key)
    return null
  }
  return item.value
}

export const generateGuid = () => {
  var result, i, j;
  result = '';
  for(j=0; j<32; j++) {
    if( j === 8 || j === 12 || j === 16 || j === 20)
      result = result + '-';
    i = Math.floor(Math.random()*16).toString(16).toUpperCase();
    result = result + i;
  }
  return result;
}
