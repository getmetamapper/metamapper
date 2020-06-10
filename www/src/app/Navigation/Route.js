import React from "react"
import { Route } from "react-router-dom"
import { Layout } from "antd"
import { Helmet } from "react-helmet"
import { UserContextProvider } from "context/UserContext"
import Navbar from "app/Navigation/Navbar"
import withSessionRequired from "hoc/withSessionRequired"

export default ({
  component: Component,
  namespace = "",
  isPublic = false,
  isProtected = true,
  ignoreRedirects = false,
  ...restProps
}) => {
  const WrappedComponent = withSessionRequired(
    Component,
    isProtected,
    ignoreRedirects,
  )
  return (
    <Route
      {...restProps}
      render={(matchProps) => (
        <Layout>
          <Helmet>
            <meta
              name="viewport"
              content={`width=device-width, initial-scale=1, shrink-to-fit=no, maximum-scale=${
                isPublic ? "1.0" : "0.4"
              }`}
            />
          </Helmet>
          <UserContextProvider>
            {!isPublic && <Navbar />}
            <Layout.Content
              className={`content ${isPublic ? "public" : "private"}`}
            >
              <Layout className={namespace}>
                <WrappedComponent {...matchProps} />
              </Layout>
            </Layout.Content>
          </UserContextProvider>
        </Layout>
      )}
    />
  )
}
