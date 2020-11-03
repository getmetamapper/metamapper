import React, { Component } from "react"
import { Button } from "antd"
import { filter, map } from "lodash"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import qs from "query-string"

class SearchEntityNavigator extends Component {
  constructor(props) {
    super(props)

    const {
      types,
    } = this.parseTypesFromQuerystring()

    const possibleTypes = [
      {
        label: "Table",
        type: "table",
      },
      {
        label: "Column",
        type: "column",
      },
      {
        label: "Discussion",
        type: "comment",
      }
    ]

    const activeTypes = filter(types, (type) => map(possibleTypes, 'type').indexOf(type) > -1)

    this.state = {
      activeTypes,
      possibleTypes,
    }
  }

  parseTypesFromQuerystring = () => {
    let { types, ...params } = qs.parse(this.props.location.search)

    if (!types) {
      types = []
    } else if (!Array.isArray(types)) {
      types = [types]
    }

    return { types, params }
  }

  handleNavigate = (type) => {
    const { currentWorkspace: { slug } } = this.props

    let { types, params } = this.parseTypesFromQuerystring()

    if (types.indexOf(type) === -1) {
      types.push(type)
    } else {
      types.splice(types.indexOf(type), 1);
    }

    this.props.history.push(`/${slug}/search/results?${qs.stringify({ types, ...params })}`)
  }

  clearNavigation = () => {
    const { currentWorkspace: { slug } } = this.props
    const { params } = this.parseTypesFromQuerystring()
    this.props.history.push(`/${slug}/search/results?${qs.stringify(params)}`)
  }

  getButtonType = (isActive) => {
    return isActive ? "primary" : "default"
  }

  render() {
    const {
      activeTypes,
      possibleTypes,
    } = this.state
    return (
      <div className="showing">
        <Button
          type={this.getButtonType(activeTypes.length === 0)}
          onClick={this.clearNavigation}
        >
          All
        </Button>
        {map(possibleTypes, ({ label, type }) => (
          <Button
            type={this.getButtonType(activeTypes.indexOf(type) > -1)}
            onClick={() => this.handleNavigate(type)}
          >
            {label}
          </Button>
        ))}
      </div>
    )
  }
}

export default withUserContext(withRouter(SearchEntityNavigator))
