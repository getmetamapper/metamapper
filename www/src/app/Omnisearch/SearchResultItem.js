import React from "react"
import { Icon, List, Row, Col, Tooltip, Tag } from "antd"
import Link from "app/Navigation/Link"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"
import Interweave from "interweave"

const iconMapping = {
  column: "project",
  table: "table",
  comment: "message",
}

const relevance = (score) => {

  if (score >= 0.06) {
    return <Tag color="geekblue">High</Tag>
  }

  if (score >= 0.02) {
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
    <Row>
      <Col span={2}>
        <Tooltip title={modelName}>
          <Icon
            type={iconMapping[modelName.toLowerCase()]}
            style={{ fontSize: 32 }}
          />
        </Tooltip>
      </Col>
      <Col span={22}>
        <p className="label">
          <Link to={pathname}><b>{label}</b></Link>
            <span style={{ float: "right" }}>
              <Tooltip title={`Revelance Score`}>
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
        </p>
        <p className="desc">
          {description ? (
            <Interweave content={description} />
          ) : (
            <span>No description provided</span>
          )}
        </p>
      </Col>
    </Row>
  </List.Item>
)

export default SearchResultItem
