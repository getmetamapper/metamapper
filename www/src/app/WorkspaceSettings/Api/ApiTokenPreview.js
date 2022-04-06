import React from "react"
import { Alert } from "antd"
import CopyInput from "app/Common/CopyInput"

const ApiTokenPreview = ({ tokenName, tokenSecret, onClose }) => (
  <div className="api-token-setup-secret">
    <Alert
      type="success"
      closable
      message={<span>API token <b>{tokenName}</b> has been created.</span>}
      description={
        <div className="api-token-setup-secret-inner">
          <p>
            Make sure to copy the access token now. You won’t be able to see it again!
          </p>
          <CopyInput value={tokenSecret} />
         </div>
      }
      onClose={onClose}
    />
  </div>
)

export default ApiTokenPreview
