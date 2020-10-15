import React, { Component } from "react"
import { Button, Icon, Table } from "antd"
import { cloneDeep, map } from "lodash"
import { CSVLink } from "react-csv"
import { copyToClipboard, generateGuid } from "lib/utilities"

class ExportableTable extends Component {
  constructor(props) {
    super(props)

    this.handleCopyToClipboard = this.handleCopyToClipboard.bind(this)
  }

  handleCopyToClipboard = () => {
    const {
      dataSource,
      headers,
    } = this.props

    const tsvHead = map(headers, "key")
    const tsvData = this.prepareDataSource(dataSource, headers)

    const stdoutHead = map(headers, "label").join("\t") + "\n"
    const stdoutData = map(tsvData, (r) => map(tsvHead, (h) => r[h]).join("\t")).join("\n")

    copyToClipboard(stdoutHead + stdoutData)
  }

  prepareDataSource = (dataSource, headers) => {
    const data = []

    for (var i = dataSource.length - 1; i >= 0; i--) {
      let object = cloneDeep(dataSource[i])
      let output = {}

      for (var j = headers.length - 1; j >= 0; j--) {
        const { key, transformColumn } = headers[j]

        if (transformColumn) {
          output[key] = transformColumn(object[key])
        } else {
          output[key] = object[key]
        }
      }

      data.push(output)
    }

    data.reverse()
    return data
  }

  render() {
    const { dataSource, headers } = this.props
    return (
      <span className="exportable-table">
        <div className="table-operations">
          <CSVLink data={this.prepareDataSource(dataSource, headers)} headers={headers} filename={`${generateGuid().toLowerCase()}.csv`}>
            <Button size="small">
              <Icon type="export" /> Export as CSV
            </Button>
          </CSVLink>
          <Button size="small" onClick={this.handleCopyToClipboard}>
            <Icon type="copy" /> Copy to Clipboard
          </Button>
        </div>
        <Table {...this.props} />
      </span>
    )
  }
}

export default ExportableTable
