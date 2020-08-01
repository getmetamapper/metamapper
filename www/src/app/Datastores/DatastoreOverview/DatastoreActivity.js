import React from "react"
import { Card, List } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreActivityItem from "./DatastoreActivityItem"

const DatastoreActivity = ({ datastore, activities, title }) => (
  <Card className="datastore-activity" title={title}>
    <List
      dataSource={activities}
      renderItem={(activity) => (
        <DatastoreActivityItem datastore={datastore} {...activity} />
      )}
    />
  </Card>
)

export default withLargeLoader(DatastoreActivity)
