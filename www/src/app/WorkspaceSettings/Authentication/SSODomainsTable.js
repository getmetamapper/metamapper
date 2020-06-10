import React, { Component } from "react"
import { Table, Tag } from "antd"
import DeleteSSODomain from "./DeleteSSODomain"
import SSODomainVerificationInstructions from "./SSODomainVerificationInstructions"

class SSODomainsTable extends Component {
  constructor(props) {
    super(props)

    this.verificationStatusColors = {
      FAILED: "red",
      PENDING: "gold",
      SUCCESS: "green",
    }

    this.columns = [
      {
        title: "Domain",
        dataIndex: "domain",
        key: "domain",
      },
      {
        title: "Verification Status",
        dataIndex: "verificationStatus",
        align: "center",
        render: (status) => (
          <Tag
            data-test="SSODomainsTable.VerificationStatus"
            color={this.verificationStatusColors[status]}
          >
            {status}
          </Tag>
        ),
      },
      {
        align: "right",
        render: ({ id, domain }) => (
          <DeleteSSODomain domainID={id} domain={domain} />
        ),
      },
    ]
  }

  render() {
    const { ssoDomains } = this.props
    return (
      <span className="sso-domains-table" data-test="SSODomainsTable">
        <Table
          rowKey="pk"
          dataSource={ssoDomains}
          columns={this.columns}
          pagination={false}
          expandedRowRender={(record) => (
            <SSODomainVerificationInstructions {...record} />
          )}
        />
      </span>
    )
  }
}

export default SSODomainsTable
// Add the following TXT record to the DNS configuration for your domain.
// The procedure for adding CNAME records depends on your DNS service Provider
// Verification can take up to 72 hours.
