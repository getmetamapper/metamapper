import React from "react"
import { Icon, List, Tooltip, Tag } from "antd"
import Link from "app/Navigation/Link"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"
import Interweave from "interweave"

const iconMapping = {
  column: "project",
  table: "table",
  comment: "message",
}

const maxDescriptionLength = 140;

const relevance = (score) => {
  if (score >= 0.66) {
    return <Tag color="geekblue">High</Tag>
  }

  if (score >= 0.33) {
    return <Tag color="volcano">Medium</Tag>
  }

  return <Tag>Low</Tag>
}

const SearchResultItem = ({
  datastore,
  score,
  modelName,
  highlightWords,
  searchResult: { label, description, pathname },
}) => (
  <List.Item className="search-result" data-test="SearchResultItem">
    <div className="search-result-icon">
      <Tooltip title={modelName}>
        <Icon
          type={iconMapping[modelName.toLowerCase()]}
          style={{ fontSize: 32 }}
        />
      </Tooltip>
    </div>
    <div className="search-result-content">
      <p className="label">
        <Link to={pathname}><b>{label}</b></Link>
      </p>
      <p className="desc">
        {description ? (
          <Interweave
            content={
              (description.length < maxDescriptionLength)
                ? description
                : `${description.substring(0, maxDescriptionLength + 1)}...`
            }
          />
        ) : (
          <span>No description provided</span>
        )}
      </p>
    </div>
    <div className="search-result-metadata">
      <span className="pull-right">
        <Tooltip title="Relevance Score">
          {relevance(score)}
        </Tooltip>
        {datastore && (
          <span className="ml-5">
            <DatastoreEngineIcon
              datastore={datastore}
              tooltip={datastore.name}
              customStyles={{
                width: 24,
                height: 24,
              }}
            />
          </span>
        )}
      </span>
    </div>
  </List.Item>
)

export default SearchResultItem
