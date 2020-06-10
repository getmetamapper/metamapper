import React from "react"
import FormLabel from "app/Common/FormLabel"
import CopyInput from "app/Common/CopyInput"
import { Form } from "antd"
import { ORIGIN_HOST } from "lib/constants"

const SamlConnectionSetupDetails = ({
  ssoConnection: { pk: ssoPrimaryKey, provider },
}) => (
  <>
    <h3>Configure Identity Provider (IdP)</h3>
    <p>Enter the following values in your identity provider.</p>
    <Form.Item>
      <FormLabel label="Single Sign-On URL" />
      <CopyInput
        value={`${ORIGIN_HOST}/saml2/acs/callback?connection=${ssoPrimaryKey}`}
      />
    </Form.Item>
    <Form.Item>
      <FormLabel label="Audience" />
      <CopyInput
        value={`urn:saml2:metamapper:${provider.toLowerCase()}-${ssoPrimaryKey}`}
      />
    </Form.Item>
  </>
)

export default SamlConnectionSetupDetails
