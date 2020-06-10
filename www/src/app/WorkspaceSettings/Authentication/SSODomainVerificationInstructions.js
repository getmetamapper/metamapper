import React from "react"
import { Table, Tooltip } from "antd"
import { copyToClipboard } from "lib/utilities"

const columns = [
  {
    title: "Host",
    dataIndex: "host",
    key: "host",
    align: "center",
  },
  {
    title: "Type",
    dataIndex: "type",
    key: "type",
    align: "center",
  },
  {
    title: "Value",
    dataIndex: "token",
    key: "token",
    render: (token) => {
      const fullToken = `metamapper-domain-verification=${token}`
      return (
        <Tooltip title="Click to copy">
          <span
            className="domain-verification-token"
            onClick={() => copyToClipboard(fullToken)}
          >
            {fullToken}
          </span>
        </Tooltip>
      )
    },
  },
]

const SSODomainVerificationInstructions = ({ verificationToken }) => (
  <div className="domain-verification-instructions">
    <p>
      Add the following TXT record to the DNS configuration for your domain.
      This procedure can depend on your DNS service provider.
    </p>
    <Table
      bordered
      size="small"
      pagination={false}
      columns={columns}
      dataSource={[
        {
          host: "@",
          type: "TXT",
          token: verificationToken,
        },
      ]}
    />
  </div>
)

export default SSODomainVerificationInstructions
