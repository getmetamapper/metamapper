import React from "react"
import { Route } from "react-router-dom"
import { Layout } from "antd"
import { Helmet } from "react-helmet"
import { UserContextProvider } from "context/UserContext"
import Navbar from "app/Navigation/Navbar"
import ErrorBoundry from "app/Errors/ErrorBoundry"
import withSessionRequired from "hoc/withSessionRequired"
import withOpensourceSetupRedirect from "hoc/withOpensourceSetupRedirect"

export default ({
  component: Component,
  namespace = "",
  isPublic = false,
  isProtected = true,
  ignoreRedirects = false,
  shouldRefreshUser = false,
  ...restProps
}) => {
  let WrappedComponent = withSessionRequired(
    Component,
    isProtected,
    ignoreRedirects,
    shouldRefreshUser
  )

  if (isPublic) {
    WrappedComponent = withOpensourceSetupRedirect(WrappedComponent, ignoreRedirects)
  }

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
                  <ErrorBoundry>
                    <WrappedComponent {...matchProps} />
                  </ErrorBoundry>
                </Layout>
              </Layout.Content>
          </UserContextProvider>
        </Layout>
      )}
    />
  )
}
