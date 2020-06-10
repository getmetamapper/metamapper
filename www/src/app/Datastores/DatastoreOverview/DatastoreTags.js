import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Tag, Icon } from "antd"
import { map, isEqual, sortBy } from "lodash"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import EditableText from "app/Common/EditableText"
import TagsInput from "app/Common/TagsInput"
import UpdateDatastoreMetadata from "graphql/mutations/UpdateDatastoreMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreTags extends Component {
  constructor(props) {
    super(props)

    this.state = {
      tags: props.datastore.tags,
      currentTags: props.datastore.tags,
    }
  }

  handleChange = (tags) => {
    this.setState({ tags })
  }

  handleSave = (e) => {
    e.preventDefault()

    const {
      datastore: { id },
    } = this.props
    const { currentTags, tags } = this.state

    const payload = {
      variables: {
        id,
        tags,
      },
      successMessage: "Tags were updated.",
    }

    if (!isEqual(sortBy(tags), sortBy(currentTags))) {
      this.props.handleMutation(payload)
    }
  }

  renderContent = (tags, hasPermission) => {
    return (
      <>
        {map(tags, (tag) => (
          <Tag color="blue" key={tag} data-test={`DatastoreTags.Tag(${tag})`}>
            {tag}
          </Tag>
        ))}
        {hasPermission && (
          <Tag
            color="purple"
            onClick={this.toggleEditTags}
            data-test="DatastoreTags.Add"
          >
            <Icon type="plus" /> Add a tag
          </Tag>
        )}
      </>
    )
  }

  render() {
    const { tags } = this.state
    const { hasPermission } = this.props
    return (
      <div className="data-asset-tags">
        <EditableText
          cypress="DatastoreTags"
          content={this.renderContent(tags, hasPermission)}
          disabled={!hasPermission}
          onClickButton={this.handleSave}
        >
          <TagsInput
            value={tags}
            disabled={!hasPermission}
            onChange={this.handleChange}
            data-test="DatastoreTags.Input"
          />
        </EditableText>
      </div>
    )
  }
}

const enhance = compose(
  withWriteAccess,
  graphql(UpdateDatastoreMetadata),
  withGraphQLMutation
)

export default enhance(DatastoreTags)
