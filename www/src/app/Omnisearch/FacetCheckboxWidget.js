import React, { Component, Fragment } from "react"
import { filter, sortBy, uniqBy } from "lodash"
import { Checkbox } from "antd"
import { withRouter } from "react-router-dom"
import qs from "query-string"
import FacetCheckboxDialog from "app/Omnisearch/FacetCheckboxDialog"

class FacetCheckboxWidget extends Component {
  constructor(props) {
    super(props)

    const current = this.getCurrentValues()
    const options = filter(props.options, (option) => {
      return current.indexOf(option.value) > -1
    })

    const availableOptions = filter(props.options, (option) => {
      return current.indexOf(option.value) < 0
    })

    for (let i = (props.limit - options.length + 1); i >= 0; i--) {
      if (availableOptions[i]) {
        options.push(availableOptions[i])
      }
    }

    this.state = {
      options: sortBy(uniqBy(options, 'value'), 'label'),
      visible: false,
    }
  }

  getCurrentValues = () => {
    const selected = qs.parse(this.props.location.search)[this.props.name]

    if (!selected) {
      return []
    }

    if (!Array.isArray(selected)) {
      return [selected]
    }

    return selected
  }

  handleClose = () => {
    this.setState({ visible: false })
  }

  handleChangeOptions = (selected) => {
    const options = filter(this.props.options, (o) => selected.indexOf(o.value) > -1)

    for (var i = 1 + this.props.limit - options.length; i >= 0; i--) {
      options.push(this.props.options[i])
    }

    this.setState({ options })

    const newValue = {}
    newValue[this.props.name] = selected

    this.props.form.setFieldsValue(newValue)
  }

  render() {
    const { form, name, title } = this.props
    if (this.state.options.length <= 0) {
      return null
    }
    return (
      <div className="facet">
        <h4>
          {title}
        </h4>
        <Fragment>
          {form.getFieldDecorator(name, {
            initialValue: qs.parse(this.props.location.search)[name]
          })(
            <Checkbox.Group options={this.state.options} />
          )}
        </Fragment>
        {this.props.options.length > this.props.limit && (
          <Fragment>
            <div className="show-more">
              <button className="link" onClick={() => this.setState({ visible: true })}>
                <small>show more</small>
              </button>
            </div>
            <FacetCheckboxDialog
              title={title}
              options={this.props.options}
              visible={this.state.visible}
              onCancel={this.handleClose}
              onChange={this.handleChangeOptions}
            />
          </Fragment>
        )}
      </div>
    )
  }
}

FacetCheckboxWidget.defaultProps = {
  limit: 3,
}

export default withRouter(FacetCheckboxWidget)
