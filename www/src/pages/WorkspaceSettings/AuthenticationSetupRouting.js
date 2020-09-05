import React from "react"
import { compose } from "react-apollo"
import { Helmet } from "react-helmet"
import { Col, Radio, Row } from "antd"
import { map } from "lodash"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import qs from "query-string"
import Link from "app/Navigation/Link"
import SSOProviderIcon from "app/WorkspaceSettings/Authentication/SSOProviderIcon"
import withGetSSOProviders from "graphql/withGetSSOProviders"
import { ORIGIN_HOST } from "lib/constants"


const navigate = (history, currentWorkspace, currentUser, provider) => {
  const stateStruct = {
    wksp: currentWorkspace.slug,
    uid: currentUser.pk,
    login: 0,
  }

  const state = window.btoa(qs.stringify(stateStruct))

  if (provider.provider.toUpperCase() === "GITHUB" && provider.clientId) {
    const redirectUri = `${ORIGIN_HOST}/oauth2/github/callback?state=${state}`

    window.location.href = `
      https://github.com/login/oauth/authorize
        ?client_id=${provider.clientId}
        &scope=user:email,read:org,repo
        &redirect_uri=${redirectUri}
    `.replace(/\s/g, "")
  } else if (provider.provider.toUpperCase() === "GOOGLE" && provider.clientId) {
    const redirectUri = `${ORIGIN_HOST}/oauth2/google/callback`

    window.location.href = `
      https://accounts.google.com/o/oauth2/auth
        ?client_id=${provider.clientId}
        &scope=email
        &access_type=offline
        &response_type=code
        &redirect_uri=${redirectUri}
        &state=${state}
    `.replace(/\s/g, "")
  } else {
    history.push(
      `/${
        currentWorkspace.slug
      }/settings/authentication/setup/${provider.provider.toLowerCase()}`
    )
  }
}

const AuthenticationSetupRouting = ({
  currentWorkspace,
  currentUser,
  history,
  ssoProviders,
}) => (
  <Row>
    <Helmet>
      <title>Authentication Setup - {currentWorkspace.slug} - Metamapper</title>
    </Helmet>
    <Col span={12} offset={6}>
      <h3 className="text-centered">Single Sign-On Setup</h3>
      <p className="text-centered mb-0">
        Select a identity provider below to start setting up a single sign-on
        for your workspace.
      </p>
      <p className="text-centered mb-0">
        <small>
          <Link to="/settings/authentication">(nevermind)</Link>
        </small>
      </p>
      <Radio.Group
        size="large"
        className="radio-icon"
        onChange={(evt) =>
          navigate(history, currentWorkspace, currentUser, evt.target.value)
        }
      >
        {map(ssoProviders, (ssoProvider) => (
          <Radio.Button value={ssoProvider}>
            <SSOProviderIcon {...ssoProvider} size={50} />
            <span className="text">{ssoProvider.label}</span>
          </Radio.Button>
        ))}
      </Radio.Group>
    </Col>
  </Row>
)

export default compose(
  withRouter,
  withUserContext,
  withGetSSOProviders,
)(AuthenticationSetupRouting)
