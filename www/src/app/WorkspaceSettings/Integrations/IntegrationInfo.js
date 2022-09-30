import React from "react"
import { Tag } from "antd"
import IntegrationIcon from "app/Integrations/IntegrationIcon"

const IntegrationInfo = ({ avatarSize, titleSize, showTags, integration }) => (
  <div className="integration">
    <div className="integration-icon">
      <IntegrationIcon
        integration={integration.id}
        customStyles={{
          height: avatarSize,
          width: avatarSize,
        }}
      />
    </div>
    <div className="integration-info">
      <span className="integration-name" style={{ fontSize: titleSize }}>
        {integration.name}
      </span>
      <span className={`integration-status ${integration.installed ? 'installed' : ''}`}>
        <div className="dot"></div>
        <div className="desc">
          {integration.installed ? 'Installed' : 'Not Installed'}
        </div>
      </span>
      {showTags && (
        <span className="integration-tags">
          {integration.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
        </span>
      )}
    </div>
  </div>
)

IntegrationInfo.defaultProps = {
  avatarSize: 40,
  titleSize: 14,
  showTags: false,
}

export default IntegrationInfo
