import React, { Component } from "react"
import { List, Icon } from "antd"
import { mapKeys } from "lodash"
import withLoader from "hoc/withLoader"

class FilterSearchByDatastore extends Component {
  constructor(props) {
    super(props)

    this.state = {
      datastoreMap: mapKeys(props.datastores, "pk"),
    }
  }

  isSelected(datastore) {
    const { selected } = this.props

    console.log(selected)

    if (!selected) {
      return false
    }

    return selected.pk === datastore.pk
  }

  handleClear = () => {
    this.props.onSelect(null)
  }

  render() {
    const { datastores } = this.props
    return (
      <List
        header="Filter by Datastore"
        bordered
        dataSource={datastores}
        renderItem={(datastore) => (
          <List.Item
            key={datastore.pk}
            className={`omnisearch-datastore ${
              this.isSelected(datastore) ? "active" : ""
            }`}
          >
            <div className="item">
              <span
                className="text"
                onClick={() => this.props.onSelect(datastore)}
              >
                {datastore.name}
              </span>
              {this.isSelected(datastore) && (
                <span className="icon" onClick={this.handleClear}>
                  <Icon type="close-circle" />
                </span>
              )}
            </div>
          </List.Item>
        )}
      />
    )
  }
}

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

export default withLargeLoader(FilterSearchByDatastore)
