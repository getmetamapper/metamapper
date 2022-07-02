import React, { Component } from "react"
import { compose } from "react-apollo"
import { Input, Form } from "antd"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import qs from "query-string"

class NavbarSearch extends Component {
  constructor(props) {
    super(props)

    const { q: query } = qs.parse(props.location.search)

    this.state = {
      query,
    }
  }

  handleSearch = (value, e) => {
    if (e.keyCode !== 13) {
      return
    }

    const {
      config,
      currentWorkspace: { slug },
      location: { search },
      history,
    } = this.props

    const params = {
      ...qs.parse(search),
      ...{ q: value },
    }

    const datastoreSlug = config.getDatastoreSlug()

    if (datastoreSlug) {
      params.datastores = datastoreSlug
    }

    history.push(`/${slug}/search/results?${qs.stringify(params)}`)
  }

  handleChange = (e) => {
    this.setState({
      query: e.target.value,
    })
  }

  render() {
    const { query } = this.state
    return (
      <Form layout="inline" id="navbar-search">
        <Input.Search
          type="text"
          placeholder="Type to search..."
          className={query ? "focused" : ""}
          value={query}
          onChange={this.handleChange}
          onSearch={this.handleSearch}
          data-test="Omnisearch.NavbarSearch"
        />
      </Form>
    )
  }
}

export default compose(withRouter, withUserContext)(NavbarSearch)
