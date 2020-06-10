import React from "react"
import { Card, List } from "antd"
import withLoader from "hoc/withLoader"
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

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

export default withLargeLoader(DatastoreActivity)
