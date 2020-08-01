import React from "react"
import moment from "moment"
import { Card, List } from "antd"
import { withLargeLoader } from "hoc/withLoader"

const UserActivityItem = ({
  actor,
  target,
  timestamp,
  verb,
  oldValues,
  newValues,
}) => {
  return (
    <List.Item className="user-activity-item">
      <List.Item.Meta
        title="hello"
        description={moment(timestamp).fromNow()}
      />
    </List.Item>
  )
}

const UserActivity = ({ activities }) => (
  <Card className="user-activity">
    <List
      dataSource={activities}
      renderItem={(activity) => (
        <UserActivityItem {...activity} />
      )}
    />
  </Card>
)

export default withLargeLoader(UserActivity)
