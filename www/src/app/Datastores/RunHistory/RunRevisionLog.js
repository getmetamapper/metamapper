import React, { Component } from "react"
import { compose } from "react-apollo"
import { debounce, map } from "lodash"
import { Drawer } from "antd"
import withGetRunRevisions from "graphql/withGetRunRevisions"
import RunRevisionLogTable from "./RunRevisionLogTable"

const defaultDrawerProps = {
  id: "run-revision-log",
  className: "revisions",
  placement: "right",
  width: "85%",
}

class RunRevisionLog extends Component {
  constructor(props) {
    super(props)

    this.state = {
      dataSource: props.runRevisions,
      loading: false,
      actions: null,
      types: null,
      search: null,
    }

    this.handleScroll = this.handleScroll.bind(this)
  }

  fetchNextPage = () => {
    this.setState({ loading: true })

    this.props.fetchNextPage().then(({ data }) => {
      const { runRevisions: { edges } } = data

      this.setState({
        loading: false,
        dataSource: [
          ...this.state.dataSource,
          ...map(edges, ({ node }) => node),
        ]
      })
    })
  }

  componentDidUpdate(nextProps, nextState) {
    if (nextState.actions !== this.state.actions || nextState.types !== this.state.types || nextState.search !== this.state.search) {
      this.applyFilters()
    }

    if (this.props.loading !== nextProps.loading || this.state.loading !== nextState.loading) {
      this.setState({
        dataSource: this.props.runRevisions
      })
    }
  }

  handleScroll = () => {
    if (this.state.loading || !this.props.hasNextPage) return;

    const parent = document.getElementById("run-revision-log")
    const documentElement = parent.getElementsByClassName("ant-drawer-wrapper-body")

    if (
      documentElement.length === 1 &&
      documentElement[0].scrollTop + documentElement[0].offsetHeight
      >= (documentElement[0].scrollHeight * 0.985)
    ) {
      this.fetchNextPage()
    }
  }

  applyFilters = () => {
    this.setState({ loading: true })

    const {
      actions,
      types,
      search,
    } = this.state

    const variables = {
      runId: this.props.run.id,
      actions: actions,
      types: types,
      search: search,
    }

    this.props.refetch(variables).then(({ data }) => {
      const { runRevisions: { edges } } = data
      this.setState({
        dataSource: map(edges, ({ node }) => node)
      })
    }).then(() => this.setState({ loading: false }))
  }

  render () {
    const { title, visible, onClose } = this.props
    const { dataSource } = this.state
    return (
      <Drawer
        visible={visible}
        onClose={onClose}
        title={title}
        onScroll={debounce(this.handleScroll, 100)}
        {...defaultDrawerProps}
      >
        <RunRevisionLogTable
          dataSource={dataSource}
          loading={this.props.loading || this.state.loading}
          onClose={onClose}
          visible={visible}
          onFilter={(state) => this.setState(state)}
        />
      </Drawer>
    )
  }
}

RunRevisionLog.defaultProps = {
  runRevisions: [],
}

export default compose(withGetRunRevisions)(RunRevisionLog)
